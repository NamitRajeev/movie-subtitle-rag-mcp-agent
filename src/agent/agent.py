# src/agent/agent.py

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.agent.clarification import ClarificationHandler
from src.agent.movie_resolver import MovieResolver
from src.agent.router import AgentRouter
from src.agent.schemas import AgentRequest
from src.agent.state import ConversationState
from src.generation.answer_generator import AnswerGenerator
from src.retrieval.citations import build_citations
from src.retrieval.retriever import Retriever


class MovieAgent:
    """
    Coordinate movie resolution, routing, RAG, conversation state,
    and MCP email actions.
    """

    def __init__(self):
        self.movie_resolver = MovieResolver()
        self.router = AgentRouter()
        self.clarification_handler = ClarificationHandler()
        self.retriever = Retriever()
        self.answer_generator = AnswerGenerator()
        self.state = ConversationState()

    @staticmethod
    def _is_email_follow_up(query: str) -> bool:
        if not query:
            return False

        normalized = query.strip().lower()

        follow_up_phrases = {
            "email me that",
            "email that",
            "email it",
            "send me that",
            "send it",
        }

        return normalized in follow_up_phrases

    async def process(self, request: AgentRequest) -> dict:

        # Handle a pending email action first.
        # This allows the user to provide only the email address
        # after the agent previously asked for it.
        if self.state.pending_action == "email_previous_result":
            if not request.recipient or not request.recipient.strip():
                return {
                    "status": "clarification",
                    "message": (
                        "What email address should I send "
                        "the previous answer to?"
                    ),
                }

            if not self.state.last_answer:
                self.state.clear_pending_action()

                return {
                    "status": "no_evidence",
                    "message": (
                        "There is no previous answer available "
                        "to email."
                    ),
                }

            movie = self.state.current_movie
            answer = self.state.last_answer
            citations = self.state.last_retrieved_sources

            email_body = self._build_email_body(
                movie=movie,
                answer=answer,
                citations=citations,
            )

            email_result = await self._send_email(
                recipient=request.recipient.strip(),
                subject=f"Scene Summary — {movie}",
                body=email_body,
            )

            self.state.clear_pending_action()

            return {
                "status": "success",
                "route": "email",
                "movie": movie,
                "answer": answer,
                "citations": citations,
                "email_result": email_result,
            }

        # Handle "Email me that" and similar follow-ups.
        if (
            request.intent == "email"
            and self._is_email_follow_up(request.query)
        ):
            if not self.state.last_answer:
                return {
                    "status": "no_previous_result",
                    "message": (
                        "There is no previous answer available "
                        "to email."
                    ),
                }

            if not request.recipient or not request.recipient.strip():
                self.state.set_pending_action(
                    "email_previous_result"
                )

                self.state.set_clarification(
                    "What email address should I send "
                    "the previous answer to?"
                )

                return {
                    "status": "clarification",
                    "message": (
                        "What email address should I send "
                        "the previous answer to?"
                    ),
                }

            movie = self.state.current_movie
            answer = self.state.last_answer
            citations = self.state.last_retrieved_sources

            email_body = self._build_email_body(
                movie=movie,
                answer=answer,
                citations=citations,
            )

            email_result = await self._send_email(
                recipient=request.recipient.strip(),
                subject=f"Scene Summary — {movie}",
                body=email_body,
            )

            return {
                "status": "success",
                "route": "email",
                "movie": movie,
                "answer": answer,
                "citations": citations,
                "email_result": email_result,
            }

        # Normal request validation.
        clarification = self.clarification_handler.check_request(
            request
        )

        if clarification["needs_clarification"]:
            self.state.set_clarification(
                clarification["question"]
            )

            return {
                "status": "clarification",
                "message": clarification["question"],
            }

        self.state.clear_clarification()

        movie_result = self.movie_resolver.resolve(
            request.movie
        )

        if movie_result["status"] == "not_found":
            return {
                "status": "not_found",
                "message": (
                    f"I couldn't find the movie "
                    f"'{request.movie}' in the indexed dataset."
                ),
            }

        if movie_result["status"] == "ambiguous":
            clarification_result = (
                self.clarification_handler.movie_clarification(
                    movie_result["candidates"]
                )
            )

            self.state.set_clarification(
                clarification_result["question"]
            )

            return {
                "status": "clarification",
                "message": clarification_result["question"],
                "candidates": movie_result["candidates"],
            }

        movie = movie_result["movie"]

        route = self.router.route(request)

        evidence = self.retriever.retrieve(
            question=request.query,
            n_results=8,
            movie=movie,
        )

        if not evidence:
            return {
                "status": "no_evidence",
                "message": (
                    "I couldn't find sufficient evidence for "
                    "that question in the indexed subtitle dataset."
                ),
                "movie": movie,
            }

        answer = self.answer_generator.generate(
            question=request.query,
            evidence=evidence,
        )

        citations = build_citations(evidence)

        # Store the successful information result so that
        # a later follow-up can refer to it as "that".
        self.state.set_request(
            movie=movie,
            query=request.query,
        )

        self.state.set_answer(answer)
        self.state.set_sources(citations)

        if route == "information":
            return {
                "status": "success",
                "route": "information",
                "movie": movie,
                "answer": answer,
                "citations": citations,
                "evidence": evidence,
            }

        if route == "email":
            email_body = self._build_email_body(
                movie=movie,
                answer=answer,
                citations=citations,
            )

            email_result = await self._send_email(
                recipient=request.recipient,
                subject=f"Scene Summary — {movie}",
                body=email_body,
            )

            return {
                "status": "success",
                "route": "email",
                "movie": movie,
                "answer": answer,
                "citations": citations,
                "email_result": email_result,
                "evidence": evidence,
            }

        raise ValueError(
            f"Unsupported route: {route}"
        )

    @staticmethod
    def _build_email_body(
        movie: str,
        answer: str,
        citations: list[str],
    ) -> str:

        body = f"Movie: {movie}\n\n"
        body += "Summary:\n"
        body += f"{answer}\n\n"
        body += "Sources:\n"

        for citation in citations:
            body += f"• {citation}\n"

        return body

    async def _send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> str:

        if not recipient:
            raise ValueError(
                "Recipient email address cannot be empty."
            )

        server_parameters = StdioServerParameters(
            command=sys.executable,
            args=["-u", "mcp/server.py"],
        )

        async with stdio_client(
            server_parameters
        ) as (read, write):

            async with ClientSession(
                read,
                write,
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    "send_email",
                    {
                        "recipient": recipient,
                        "subject": subject,
                        "body": body,
                    },
                )

                if result.is_error:
                    raise RuntimeError(
                        "MCP send_email tool returned an error."
                    )

                for content in result.content:
                    if hasattr(content, "text"):
                        return content.text

                return "Email sent successfully."


def run_agent(request: AgentRequest) -> dict:
    return asyncio.run(
        MovieAgent().process(request)
    )