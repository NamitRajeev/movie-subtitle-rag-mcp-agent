import re

from src.retrieval.vector_store import VectorStore


class MovieResolver:
    def __init__(self, vector_store=None):
        self.vector_store = vector_store or VectorStore()

    @staticmethod
    def normalize(text: str) -> str:
        """
        Normalize text for comparison.

        Converts to lowercase, replaces common filename separators
        with spaces, removes punctuation, and collapses whitespace.
        """
        text = text.lower()

        # Replace common filename separators with spaces.
        text = re.sub(r"[._-]+", " ", text)

        # Remove remaining punctuation.
        text = re.sub(r"[^\w\s]", " ", text)

        # Collapse repeated whitespace.
        text = re.sub(r"\s+", " ", text).strip()

        return text

    @classmethod
    def title_tokens(cls, movie: str) -> list[str]:
        """
        Extract the meaningful title tokens from a canonical movie ID.

        Stops at the first year token such as 2008, 2018, etc.
        """
        tokens = cls.normalize(movie).split()

        title_tokens = []

        for token in tokens:
            if re.fullmatch(r"(19|20)\d{2}", token):
                break
            title_tokens.append(token)

        return title_tokens

    def resolve(self, movie_name: str) -> dict:
        """
        Resolve a user-provided movie name against movies
        currently stored in ChromaDB.

        Returns:
            {
                "status": "resolved" | "ambiguous" | "not_found",
                "movie": canonical_movie_id | None,
                "candidates": list[str]
            }
        """

        if not movie_name or not movie_name.strip():
            return {
                "status": "not_found",
                "movie": None,
                "candidates": [],
            }

        movies = self.vector_store.get_movies()

        if not movies:
            return {
                "status": "not_found",
                "movie": None,
                "candidates": [],
            }

        normalized_input = self.normalize(movie_name)
        input_tokens = normalized_input.split()

        # 1. Exact normalized match
        exact_matches = [
            movie
            for movie in movies
            if self.normalize(movie) == normalized_input
        ]

        if len(exact_matches) == 1:
            return {
                "status": "resolved",
                "movie": exact_matches[0],
                "candidates": [],
            }

        # 2. Match against the actual movie title
        title_matches = []

        for movie in movies:
            title_tokens = self.title_tokens(movie)

            if input_tokens == title_tokens:
                title_matches.append(movie)

        if len(title_matches) == 1:
            return {
                "status": "resolved",
                "movie": title_matches[0],
                "candidates": [],
            }

        if len(title_matches) > 1:
            return {
                "status": "ambiguous",
                "movie": None,
                "candidates": title_matches,
            }

        # 3. Partial title match
        partial_matches = []

        for movie in movies:
            title_tokens = self.title_tokens(movie)

            if all(
                word in title_tokens
                for word in input_tokens
            ):
                partial_matches.append(movie)

        if len(partial_matches) == 1:
            return {
                "status": "resolved",
                "movie": partial_matches[0],
                "candidates": [],
            }

        if len(partial_matches) > 1:
            return {
                "status": "ambiguous",
                "movie": None,
                "candidates": partial_matches,
            }

        # 4. No match
        return {
            "status": "not_found",
            "movie": None,
            "candidates": [],
        }