# scripts/test_agent_email.py

from src.agent.agent import run_agent
from src.agent.schemas import AgentRequest


def main():
    request = AgentRequest(
        intent="email",
        movie="Infinity War",
        query="What does Thanos want from the Avengers?",
        recipient="rpptr0namit@gmail.com",
    )

    print("=" * 60)
    print("RAG + MCP EMAIL INTEGRATION TEST")
    print("=" * 60)

    print("\nRequest:")
    print(request)

    result = run_agent(request)

    print("\n" + "=" * 60)
    print("AGENT RESULT")
    print("=" * 60)

    print(f"\nStatus: {result['status']}")
    print(f"Route: {result.get('route')}")
    print(f"Movie: {result.get('movie')}")

    if result["status"] == "success":
        print("\nAnswer:")
        print(result["answer"])

        print("\nCitations:")
        for citation in result["citations"]:
            print(f"• {citation}")

        if result.get("route") == "email":
            print("\nEmail result:")
            print(result["email_result"])

    else:
        print("\nMessage:")
        print(result["message"])


if __name__ == "__main__":
    main()