from src.retrieval.retriever import Retriever


question = "What does Thanos want from the Avengers?"

retriever = Retriever()

evidence = retriever.retrieve(
    question,
    n_results=5,
)


print("\nRetrieved Evidence:")
print("=" * 60)

for i, result in enumerate(evidence, start=1):

    print(f"\nResult {i}")
    print(f"Movie: {result['movie']}")
    print(
        f"Time: "
        f"{result['start_time']} -> "
        f"{result['end_time']}"
    )
    print(f"Chunk ID: {result['chunk_id']}")
    print(f"Score: {result['score']:.4f}")

    print("\nText:")
    print(result["text"])