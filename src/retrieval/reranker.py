# src/retrieval/reranker.py

import re


class EvidenceReranker:
    def __init__(
        self,
        semantic_weight=0.7,
        keyword_weight=0.3,
    ):
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )

        stopwords = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "do",
            "does",
            "for",
            "from",
            "he",
            "how",
            "i",
            "in",
            "is",
            "it",
            "of",
            "on",
            "or",
            "that",
            "the",
            "this",
            "to",
            "was",
            "what",
            "when",
            "where",
            "who",
            "why",
            "with",
            "you",
        }

        return {
            word
            for word in words
            if word not in stopwords
        }

    def _keyword_overlap(
        self,
        question: str,
        evidence_text: str,
    ) -> float:
        question_words = self._tokenize(question)
        evidence_words = self._tokenize(evidence_text)

        if not question_words:
            return 0.0

        overlap = question_words.intersection(
            evidence_words
        )

        return len(overlap) / len(question_words)

    @staticmethod
    def _semantic_scores(
        distances: list[float],
    ) -> list[float]:
        if not distances:
            return []

        minimum = min(distances)
        maximum = max(distances)

        if minimum == maximum:
            return [1.0] * len(distances)

        return [
            (maximum - distance)
            / (maximum - minimum)
            for distance in distances
        ]

    def rerank(
        self,
        question: str,
        evidence: list[dict],
        question_type: str = "other",
    ) -> list[dict]:
        if not evidence:
            return []

        distances = [
            item["score"]
            for item in evidence
        ]

        semantic_scores = self._semantic_scores(
            distances
        )

        ranked_evidence = []

        for item, semantic_score in zip(
            evidence,
            semantic_scores,
        ):
            keyword_score = self._keyword_overlap(
                question,
                item["text"],
            )

            final_score = (
                self.semantic_weight * semantic_score
                + self.keyword_weight * keyword_score
            )

            ranked_item = item.copy()
            ranked_item["question_type"] = question_type
            ranked_item["semantic_score"] = semantic_score
            ranked_item["keyword_score"] = keyword_score
            ranked_item["rerank_score"] = final_score

            ranked_evidence.append(ranked_item)

        ranked_evidence.sort(
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        return ranked_evidence