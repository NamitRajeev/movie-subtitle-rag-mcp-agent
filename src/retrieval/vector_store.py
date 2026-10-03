import chromadb


class VectorStore:
    def __init__(
        self,
        persist_directory="chroma_db",
        collection_name="movie_subtitles",
    ):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_chunks(self, chunks, embeddings):
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings."
            )

        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]

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

    def count(self):
        return self.collection.count()

    def get_movies(self) -> list[str]:
        """
        Return all unique movie identifiers currently stored in ChromaDB.
        """

        results = self.collection.get(
            include=["metadatas"]
        )

        movies = {
            metadata["movie"]
            for metadata in results["metadatas"]
            if metadata and metadata.get("movie")
        }

        return sorted(movies)

    def query(self, query_embedding, n_results=5, movie=None):
        where = None

        if movie:
            where = {"movie": movie}

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )