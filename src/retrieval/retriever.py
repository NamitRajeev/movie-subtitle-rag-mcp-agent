# src/retrieval/retriever.py

from src.retrieval.embedding import EmbeddingModel
from src.retrieval.reranker import EvidenceReranker
from src.retrieval.vector_store import VectorStore


class Retriever:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()
        self.reranker = EvidenceReranker()

    def retrieve(
        self,
        question,
        n_results=8,
        movie=None,
    ):
        query_embedding = self.embedding_model.encode(
            [question]
        )[0]

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

        reranked_evidence = self.reranker.rerank(
            question=question,
            evidence=evidence,
        )

        return reranked_evidence[:3]