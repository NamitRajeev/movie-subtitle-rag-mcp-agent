# scripts/test_followup.py

import asyncio

from src.agent.agent import MovieAgent
from src.agent.schemas import AgentRequest


async def fake_send_email(
    recipient: str,
    subject: str,
    body: str,
) -> str:
    print("\n--- Fake Email ---")
    print(f"Recipient: {recipient}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")
    print("------------------")

    return "Test email sent successfully."


async def main():
    agent = MovieAgent()

    # ---------------------------------------------------------
    # Step 1: Ask a normal movie question
    # ---------------------------------------------------------

    question_request = AgentRequest(
        intent="information",
        movie="Avengers Infinity War",
        query="What does Thanos want from the Avengers?",
    )

    print("STEP 1: Asking movie question...")

    result_1 = await agent.process(
        question_request
    )

    print("\nResult 1:")
    print(result_1["status"])
    print(result_1.get("answer"))

    if result_1["status"] != "success":
        raise AssertionError(
            "Step 1 failed: movie question did not succeed."
        )

    # ---------------------------------------------------------
    # Step 2: User says "Email me that"
    # ---------------------------------------------------------

    follow_up_request = AgentRequest(
        intent="email",
        movie=None,
        query="Email me that",
        recipient=None,
    )

    print("\nSTEP 2: Asking to email previous answer...")

    result_2 = await agent.process(
        follow_up_request
    )

    print("\nResult 2:")
    print(result_2)

    if result_2["status"] != "clarification":
        raise AssertionError(
            "Step 2 failed: agent should ask for email address."
        )

    if "email address" not in result_2["message"].lower():
        raise AssertionError(
            "Step 2 failed: expected email-address clarification."
        )

    # ---------------------------------------------------------
    # Step 3: Provide email address
    # ---------------------------------------------------------

    agent._send_email = fake_send_email

    email_request = AgentRequest(
        intent="email",
        movie=None,
        query="",
        recipient="test@example.com",
    )

    print("\nSTEP 3: Providing email address...")

    result_3 = await agent.process(
        email_request
    )

    print("\nResult 3:")
    print(result_3)

    if result_3["status"] != "success":
        raise AssertionError(
            "Step 3 failed: previous answer was not emailed."
        )

    if result_3["route"] != "email":
        raise AssertionError(
            "Step 3 failed: route should be email."
        )

    print("\nFOLLOW-UP TEST PASSED.")


if __name__ == "__main__":
    asyncio.run(main())