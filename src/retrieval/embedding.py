from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Wrapper around the Sentence Transformers embedding model.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        """
        Convert a list of texts into embedding vectors.
        """

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()