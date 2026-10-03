# scripts/test_state.py

from src.agent.state import ConversationState


def main():
    state = ConversationState()

    print("=" * 60)
    print("CONVERSATION STATE TEST")
    print("=" * 60)

    print("\nInitial state:")
    print(state.get_state())

    state.set_request(
        movie="Avengers.Infinity.War.2018.1080p.BluRay.x265-YAWNTiC_eng",
        query="What does Thanos want?",
    )

    print("\nAfter setting request:")
    print(state.get_state())

    state.set_answer(
        "Thanos wants to collect all six Infinity Stones."
    )

    print("\nAfter setting answer:")
    print(state.get_state())

    state.set_sources(
        [
            {
                "movie": "Avengers.Infinity.War.2018.1080p.BluRay.x265-YAWNTiC_eng",
                "start_time": "00:05:10",
                "end_time": "00:06:02",
                "chunk_id": "chunk_001",
            }
        ]
    )

    print("\nAfter setting sources:")
    print(state.get_state())

    state.set_clarification(
        "Which Iron Man movie do you mean?"
    )

    print("\nAfter setting clarification:")
    print(state.get_state())

    state.clear_clarification()

    print("\nAfter clearing clarification:")
    print(state.get_state())

    state.clear()

    print("\nAfter clearing entire state:")
    print(state.get_state())


if __name__ == "__main__":
    main()