# scripts/test_agent.py

import asyncio
import sys
from pathlib import Path


# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.agent.agent import MovieAgent
from src.agent.schemas import AgentRequest


def create_test_agent():
    agent = MovieAgent()

    class FakeRetriever:
        def retrieve(
            self,
            question,
            n_results=8,
            movie=None,
        ):
            return [
                {
                    "text": (
                        "Thanos wants to bring balance "
                        "to the universe."
                    ),
                    "movie": movie,
                    "start_time": "00:10:00",
                    "end_time": "00:11:00",
                    "chunk_id": "test_chunk_1",
                    "score": 0.1,
                }
            ]

    class FakeAnswerGenerator:
        def generate(
            self,
            question,
            evidence,
        ):
            return (
                "Thanos wants to bring balance "
                "to the universe."
            )

    agent.retriever = FakeRetriever()
    agent.answer_generator = FakeAnswerGenerator()

    return agent


def test_information_request():
    agent = create_test_agent()

    request = AgentRequest(
        intent="information",
        movie="Avengers Infinity War",
        query="What does Thanos want?",
    )

    result = asyncio.run(
        agent.process(request)
    )

    assert result["status"] == "success"
    assert result["route"] == "information"
    assert result["movie"] == (
        "Avengers.Infinity.War.2018.1080p."
        "BluRay.x265-YAWNTiC_eng"
    )
    assert "Thanos" in result["answer"]
    assert result["citations"]


def test_missing_movie():
    agent = create_test_agent()

    request = AgentRequest(
        intent="information",
        movie=None,
        query="What happens?",
    )

    result = asyncio.run(
        agent.process(request)
    )

    assert result["status"] == "clarification"
    assert "movie" in result["message"].lower()


def test_missing_query():
    agent = create_test_agent()

    request = AgentRequest(
        intent="information",
        movie="Avengers Infinity War",
        query="",
    )

    result = asyncio.run(
        agent.process(request)
    )

    assert result["status"] == "clarification"
    assert "know" in result["message"].lower()


def test_unknown_movie():
    agent = create_test_agent()

    request = AgentRequest(
        intent="information",
        movie="Spider-Man",
        query="What happens?",
    )

    result = asyncio.run(
        agent.process(request)
    )

    assert result["status"] == "not_found"


def test_missing_email_recipient():
    agent = create_test_agent()

    request = AgentRequest(
        intent="email",
        movie="Avengers Infinity War",
        query="What does Thanos want?",
        recipient=None,
    )

    result = asyncio.run(
        agent.process(request)
    )

    assert result["status"] == "clarification"
    assert "email address" in result["message"].lower()


def test_email_follow_up():
    agent = create_test_agent()

    sent = {}

    async def fake_send_email(
        recipient,
        subject,
        body,
    ):
        sent["recipient"] = recipient
        sent["subject"] = subject
        sent["body"] = body

        return "Test email sent successfully."

    agent._send_email = fake_send_email

    # First turn: obtain an answer.
    question_request = AgentRequest(
        intent="information",
        movie="Avengers Infinity War",
        query="What does Thanos want?",
    )

    first_result = asyncio.run(
        agent.process(question_request)
    )

    assert first_result["status"] == "success"

    # Second turn: "Email me that".
    follow_up_request = AgentRequest(
        intent="email",
        movie=None,
        query="Email me that",
        recipient=None,
    )

    second_result = asyncio.run(
        agent.process(follow_up_request)
    )

    assert second_result["status"] == "clarification"
    assert "email address" in second_result["message"].lower()

    # Third turn: provide recipient.
    recipient_request = AgentRequest(
        intent="email",
        movie=None,
        query="",
        recipient="test@example.com",
    )

    third_result = asyncio.run(
        agent.process(recipient_request)
    )

    assert third_result["status"] == "success"
    assert third_result["route"] == "email"

    assert sent["recipient"] == "test@example.com"

    assert (
        "Thanos wants to bring balance"
        in sent["body"]
    )

    assert "Sources:" in sent["body"]


def test_follow_up_without_previous_answer():
    agent = create_test_agent()

    request = AgentRequest(
        intent="email",
        movie=None,
        query="Email me that",
        recipient=None,
    )

    result = asyncio.run(
        agent.process(request)
    )

    assert result["status"] == "no_previous_result"


if __name__ == "__main__":
    print(
        "Run this file with pytest:"
    )
    print(
        "pytest scripts/test_agent.py -v"
    )