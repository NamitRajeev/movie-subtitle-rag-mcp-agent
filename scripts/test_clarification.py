# scripts/test_clarification.py

from src.agent.clarification import ClarificationHandler
from src.agent.schemas import AgentRequest


def main():
    handler = ClarificationHandler()

    complete_request = AgentRequest(
        intent="information",
        movie="Avengers.Infinity.War.2018.1080p.BluRay.x265-YAWNTiC_eng",
        query="What does Thanos want?",
    )

    missing_movie_request = AgentRequest(
        intent="information",
        movie=None,
        query="What does Thanos want?",
    )

    missing_recipient_request = AgentRequest(
        intent="email",
        movie="Avengers.Infinity.War.2018.1080p.BluRay.x265-YAWNTiC_eng",
        query="What does Thanos want?",
        recipient=None,
    )

    print("=" * 60)
    print("CLARIFICATION TEST")
    print("=" * 60)

    print("\nComplete request:")
    print(handler.check_request(complete_request))

    print("\nMissing movie:")
    print(handler.check_request(missing_movie_request))

    print("\nMissing recipient:")
    print(handler.check_request(missing_recipient_request))

    print("\nAmbiguous movie:")
    candidates = [
        "Iron.Man.2008.1080p.BluRay.x265-YAWNTiC_eng",
        "Iron.Man.2.2010.1080p.BluRay.x265-YAWNTiC_eng",
        "Iron.Man.3.2013.1080p.BluRay.x265-YAWNTiC_eng",
    ]

    print(handler.movie_clarification(candidates))


if __name__ == "__main__":
    main()