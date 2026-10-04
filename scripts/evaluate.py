from src.agent.movie_resolver import MovieResolver
from src.generation.answer_generator import AnswerGenerator
from src.retrieval.citations import build_citations
from src.retrieval.retriever import Retriever


TEST_CASES = [
    {
        "test": 1,
        "movie": "Infinity War",
        "question": "What does Thanos want from the Avengers?",
    },
    {
        "test": 2,
        "movie": "Infinity War",
        "question": "Why does Thanos believe his plan is necessary?",
    },
    {
        "test": 3,
        "movie": "Infinity War",
        "question": "What happens when Thanos arrives on Titan?",
    },
    {
        "test": 4,
        "movie": "Infinity War",
        "question": "What does Thanos say about Gamora?",
    },
    {
        "test": 5,
        "movie": "Iron Man",
        "question": "Why does Tony Stark build the Iron Man suit?",
    },
    {
        "test": 6,
        "movie": "Endgame",
        "question": "What does the Avengers' time travel plan involve?",
    },
    {
        "test": 7,
        "movie": "Infinity War",
        "question": "What happens after Thanos gets the Time Stone?",
    },
    {
        "test": 8,
        "movie": "Infinity War",
        "question": "What was Thanos's childhood like?",
    },
    {
        "test": 9,
        "movie": "Iron Man 2",
        "question": "Who is Ivan Vanko?",
    },
    {
        "test": 10,
        "movie": "Endgame",
        "question": "Why do the Avengers decide to use time travel?",
    },
]


def main():
    retriever = Retriever()

    movie_resolver = MovieResolver(
        vector_store=retriever.vector_store
    )

    answer_generator = AnswerGenerator()

    print("=" * 70)
    print("MOVIE SUBTITLE RAG EVALUATION")
    print("=" * 70)

    for test_case in TEST_CASES:
        test_number = test_case["test"]
        movie_name = test_case["movie"]
        question = test_case["question"]

        print("\n" + "=" * 70)
        print(f"TEST {test_number}")
        print("=" * 70)

        print(f"Movie: {movie_name}")
        print(f"Question: {question}")

        # -----------------------------------------------------
        # Movie Resolution
        # -----------------------------------------------------

        movie_result = movie_resolver.resolve(
            movie_name
        )

        if movie_result["status"] != "resolved":
            print(
                f"\nMovie Resolution: "
                f"{movie_result['status']}"
            )

            if movie_result.get("candidates"):
                print("Candidates:")

                for candidate in movie_result["candidates"]:
                    print(f"• {candidate}")

            continue

        movie = movie_result["movie"]

        # -----------------------------------------------------
        # Retrieval
        # -----------------------------------------------------

        evidence = retriever.retrieve(
            question=question,
            n_results=5,
            movie=movie,
        )

        if not evidence:
            print("\nNo evidence was retrieved.")
            continue

        # -----------------------------------------------------
        # Generation
        # -----------------------------------------------------

        answer = answer_generator.generate(
            question=question,
            evidence=evidence,
        )

        # -----------------------------------------------------
        # Answer
        # -----------------------------------------------------

        print("\nAnswer:")
        print(answer)

        # -----------------------------------------------------
        # Retrieval quality summary
        # -----------------------------------------------------

        best_distance = min(
            item["score"]
            for item in evidence
        )

        print(
            f"\nTop retrieval distance: "
            f"{best_distance:.4f}"
        )

        print(
            f"Evidence retrieved: "
            f"{len(evidence)}"
        )

        # -----------------------------------------------------
        # Citations
        # -----------------------------------------------------

        citations = build_citations(
            evidence
        )

        print("\nSources:")

        for citation in citations:
            print(f"• {citation}")

    print("\n" + "=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()