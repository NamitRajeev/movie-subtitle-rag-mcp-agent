import ollama


class AnswerGenerator:
    """
    Generate grounded answers using a local Ollama model.
    """

    def __init__(
        self,
        model: str = "qwen2.5:3b",
    ):
        self.model = model

    def generate(
        self,
        question: str,
        evidence: list[dict],
    ) -> str:
        """
        Generate an answer using only the retrieved subtitle evidence.
        """

        if not evidence:
            return (
                "I couldn't find enough relevant subtitle "
                "evidence to answer that."
            )

        evidence_text = "\n\n".join(
            (
                f"Movie: {item['movie']}\n"
                f"Time: {item['start_time']} -> "
                f"{item['end_time']}\n"
                f"Dialogue:\n{item['text']}"
            )
            for item in evidence
        )

        system_prompt = """
You are a movie subtitle question-answering assistant.

Answer the user's question using ONLY the supplied subtitle evidence.

Rules:
1. Do not use outside knowledge.
2. Do not invent dialogue, events, characters, or details.
3. Do not assume facts that are not supported by the evidence.
4. If the evidence is insufficient, say:
   "The available subtitle evidence is insufficient to answer that."
5. Answer directly and concisely.
6. Do not create or guess timestamps.
7. Do not create or guess citations.
"""

        user_prompt = f"""
Question:
{question}

Retrieved subtitle evidence:
{evidence_text}

Answer the question using only the evidence above.
"""

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        return response["message"]["content"].strip()