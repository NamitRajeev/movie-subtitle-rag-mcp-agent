# scripts/test_router.py

from src.agent.router import AgentRouter
from src.agent.schemas import AgentRequest


def main():
    router = AgentRouter()

    information_request = AgentRequest(
        intent="information",
        movie="Avengers.Infinity.War.2018.1080p.BluRay.x265-YAWNTiC_eng",
        query="What does Thanos want from the Avengers?",
    )

    email_request = AgentRequest(
        intent="email",
        movie="Avengers.Infinity.War.2018.1080p.BluRay.x265-YAWNTiC_eng",
        query="What happens when Thanos arrives on Titan?",
        recipient="example@gmail.com",
    )

    print("=" * 60)
    print("ROUTER TEST")
    print("=" * 60)

    print("\nInformation request:")
    print(information_request)
    print("Route:", router.route(information_request))

    print("\nEmail request:")
    print(email_request)
    print("Route:", router.route(email_request))


if __name__ == "__main__":
    main()