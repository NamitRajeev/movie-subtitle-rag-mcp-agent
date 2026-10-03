# src/agent/router.py

from src.agent.schemas import AgentRequest


class AgentRouter:
    """
    Decide which workflow should handle an AgentRequest.
    """

    def route(self, request: AgentRequest) -> str:
        """
        Return the workflow name for the request.

        Possible routes:
            - information
            - email
        """

        if request.intent == "information":
            return "information"

        if request.intent == "email":
            return "email"

        # This should normally be unreachable because
        # AgentRequest validates the intent with Literal.
        raise ValueError(f"Unsupported intent: {request.intent}")