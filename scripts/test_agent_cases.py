# scripts/test_agent_cases.py

from src.agent.agent import run_agent
from src.agent.schemas import AgentRequest


def run_test(name, request):
    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    print("\nRequest:")
    print(request)

    try:
        result = run_agent(request)

        print("\nResult:")
        print(f"Status: {result.get('status')}")
        print(f"Route: {result.get('route')}")
        print(f"Movie: {result.get('movie')}")
        print(f"Message: {result.get('message')}")

        if result.get("status") == "success":
            print(f"Answer: {result.get('answer')}")
            print(f"Email result: {result.get('email_result')}")

    except Exception as exc:
        print(f"\nERROR: {type(exc).__name__}: {exc}")


def main():
    # 1. Normal information request
    run_test(
        "TEST 1 — Information Request",
        AgentRequest(
            intent="information",
            movie="Infinity War",
            query="What does Thanos want from the Avengers?",
        ),
    )

    # 2. Normal email request
    run_test(
        "TEST 2 — Email Request",
        AgentRequest(
            intent="email",
            movie="Infinity War",
            query="What does Thanos want from the Avengers?",
            recipient="rpptr0namit@gmail.com",
        ),
    )

    # 3. Movie not found
    run_test(
        "TEST 3 — Movie Not Found",
        AgentRequest(
            intent="information",
            movie="The Batman",
            query="Who is Batman?",
        ),
    )

    # 4. Missing movie
    run_test(
        "TEST 4 — Missing Movie",
        AgentRequest(
            intent="information",
            movie=None,
            query="What does Thanos want?",
        ),
    )

    # 5. Missing query
    run_test(
        "TEST 5 — Missing Query",
        AgentRequest(
            intent="information",
            movie="Infinity War",
            query="",
        ),
    )

    # 6. Email request without recipient
    run_test(
        "TEST 6 — Missing Email Recipient",
        AgentRequest(
            intent="email",
            movie="Infinity War",
            query="What does Thanos want?",
            recipient=None,
        ),
    )


if __name__ == "__main__":
    main()