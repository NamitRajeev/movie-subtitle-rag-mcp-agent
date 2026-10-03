# src/agent/clarification.py

from src.agent.schemas import AgentRequest


class ClarificationHandler:
    """
    Determine whether an AgentRequest needs clarification
    before the agent can continue.
    """

    def check_request(self, request: AgentRequest) -> dict:
        """
        Check whether the request contains the information
        required for its intended workflow.

        Returns:
            {
                "needs_clarification": bool,
                "question": str | None
            }
        """

        # Every request needs a query.
        if not request.query or not request.query.strip():
            return {
                "needs_clarification": True,
                "question": "What would you like to know?",
            }

        # Movie is required for both information and email
        # workflows in the current project.
        if not request.movie or not request.movie.strip():
            return {
                "needs_clarification": True,
                "question": "Which movie do you mean?",
            }

        # Email requests additionally require a recipient.
        if request.intent == "email":
            if not request.recipient or not request.recipient.strip():
                return {
                    "needs_clarification": True,
                    "question": "What email address should I send it to?",
                }

        return {
            "needs_clarification": False,
            "question": None,
        }

    def movie_clarification(self, candidates: list[str]) -> dict:
        """
        Create a clarification question when multiple movies
        match the user's input.
        """

        if not candidates:
            return {
                "needs_clarification": True,
                "question": "Which movie do you mean?",
            }

        options = ", ".join(candidates)

        return {
            "needs_clarification": True,
            "question": f"Which movie do you mean: {options}?",
        }