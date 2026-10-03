import chromadb


class VectorStore:
    """
    ChromaDB vector store for movie subtitle chunks.
    """

    def __init__(
        self,
        persist_directory: str = "chroma_db",
        collection_name: str = "movie_subtitles",
    ):
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> None:
        """
        Add subtitle chunks, embeddings, and metadata to ChromaDB.
        """

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings."
            )

        ids = [
            chunk["chunk_id"]
            for chunk in chunks
        ]

        documents = [
            chunk["text"]
            for chunk in chunks
        ]

        metadatas = [
            {
                "movie": chunk["movie"],
                "chunk_id": chunk["chunk_id"],
                "start_time": chunk["start_time"],
                "end_time": chunk["end_time"],
                "subtitle_start_id": chunk["subtitle_ids"][0],
                "subtitle_end_id": chunk["subtitle_ids"][-1],
            }
            for chunk in chunks
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def count(self) -> int:
        """Return the number of stored chunks."""

        return self.collection.count()

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> dict:
        """
        Retrieve the most relevant subtitle chunks.
        """

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )