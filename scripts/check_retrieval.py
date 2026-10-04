from src.retrieval.embedding import EmbeddingModel
from src.retrieval.vector_store import VectorStore


question = "What does Thanos want from the Avengers?"


# Create embedding model
embedding_model = EmbeddingModel()

# Convert the question into an embedding
query_embedding = embedding_model.encode([question])[0]


# Connect to ChromaDB
vector_store = VectorStore()


# Search for the most relevant chunks
results = vector_store.query(
    query_embedding,
    n_results=5,
)


# Display results
print("\nRetrieved Chunks:")
print("=" * 60)

for i in range(5):
    print(f"\nResult {i + 1}")

    metadata = results["metadatas"][0][i]
    document = results["documents"][0][i]
    distance = results["distances"][0][i]

    print(f"Movie: {metadata['movie']}")
    print(
        f"Time: "
        f"{metadata['start_time']} -> "
        f"{metadata['end_time']}"
    )
    print(f"Distance: {distance:.4f}")

    print("\nDialogue:")
    print(document)