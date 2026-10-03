from src.retrieval.retriever import Retriever
from tests.retrieval_questions import retrieval_questions


retriever = Retriever()

passed = 0

print("=" * 70)
print("RETRIEVAL EVALUATION")
print("=" * 70)

for i, item in enumerate(retrieval_questions, start=1):

    question = item["question"]
    expected_movie = item["movie"]

    results = retriever.retrieve(
        question,
        n_results=5,
        movie=expected_movie,
    )

    movie_match = bool(results) and all(
        result["movie"] == expected_movie
        for result in results
    )

    print(f"\nQuestion {i}: {question}")
    print(f"Expected movie: {expected_movie}")

    if movie_match:
        print("Movie filter: PASS")
        passed += 1
    else:
        print("Movie filter: FAIL")

    for rank, result in enumerate(results, start=1):
        print(
            f"  {rank}. "
            f"{result['start_time']} -> "
            f"{result['end_time']} | "
            f"distance={result['score']:.4f}"
        )

print("\n" + "=" * 70)
print(
    f"Movie-filter tests passed: "
    f"{passed}/{len(retrieval_questions)}"
)
print("=" * 70)