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
        movie: str | None = None,
    ) -> list[dict]:
        """
        Retrieve the most relevant subtitle chunks for a question.

        If a movie is provided, restrict retrieval to that movie.
        """

        # Convert the question into an embedding
        query_embedding = self.embedding_model.encode(
            [question]
        )[0]

        # Search ChromaDB
        results = self.vector_store.query(
            query_embedding,
            n_results=n_results,
            movie=movie,
        )

        evidence = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            evidence.append(
                {
                    "text": document,
                    "movie": metadata["movie"],
                    "start_time": metadata["start_time"],
                    "end_time": metadata["end_time"],
                    "chunk_id": metadata["chunk_id"],
                    "score": distance,
                }
            )

        return evidence