from src.retrieval.retriever import Retriever


question = "What does Thanos want from the Avengers?"

movie = (
    "Avengers.Infinity.War.2018."
    "1080p.BluRay.x265-YAWNTiC_eng"
)


retriever = Retriever()


# Retrieve without movie filtering
print("\nRetrieval without movie filter")
print("=" * 60)

results = retriever.retrieve(
    question,
    n_results=5,
)


for i, result in enumerate(results, start=1):

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


# Retrieve with movie filtering
print("\n\nRetrieval with movie filter")
print("=" * 60)

results = retriever.retrieve(
    question,
    n_results=5,
    movie=movie,
)


for i, result in enumerate(results, start=1):

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