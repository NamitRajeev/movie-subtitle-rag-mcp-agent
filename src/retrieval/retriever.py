from src.retrieval.embedding import EmbeddingModel
from src.retrieval.vector_store import VectorStore


class Retriever:
    """
    Retrieve relevant subtitle chunks from ChromaDB.
    """

    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()

    def retrieve(
        self,
        question: str,
        n_results: int = 5,
    ) -> list[dict]:
        """
        Retrieve the most relevant subtitle chunks for a question.
        """

        # Convert the question into an embedding
        query_embedding = self.embedding_model.encode(
            [question]
        )[0]

        # Search ChromaDB
        results = self.vector_store.query(
            query_embedding,
            n_results=n_results,
        )

        evidence = []

        for i in range(len(results["documents"][0])):
            metadata = results["metadatas"][0][i]

            evidence.append(
                {
                    "text": results["documents"][0][i],
                    "movie": metadata["movie"],
                    "start_time": metadata["start_time"],
                    "end_time": metadata["end_time"],
                    "chunk_id": metadata["chunk_id"],
                    "score": results["distances"][0][i],
                }
            )

        return evidence