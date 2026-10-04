# src/generation/answer_generator.py

import ollama


class AnswerGenerator:
    def __init__(
        self,
        model_name="qwen2.5:3b",
    ):
        self.model_name = model_name

    def generate(
        self,
        question: str,
        evidence: list[dict],
    ) -> str:

        if not evidence:
            return (
                "The available subtitle evidence is "
                "insufficient to answer that."
            )

        evidence_text = ""

        for index, item in enumerate(
            evidence,
            start=1,
        ):
            evidence_text += (
                f"\n--- Evidence {index} ---\n"
                f"Movie: {item['movie']}\n"
                f"Timestamp: "
                f"{item['start_time']} -> {item['end_time']}\n"
                f"Subtitle text:\n"
                f"{item['text']}\n"
            )

        prompt = f"""
You are a movie question-answering assistant.

Answer the user's question using ONLY the supplied subtitle evidence.

USER QUESTION:
{question}

SUBTITLE EVIDENCE:
{evidence_text}

GROUNDING RULES:

1. Use only information explicitly supported by the subtitle evidence.

2. Do not use your general knowledge about the movie.

3. Carefully distinguish between:
   - an actual event or confirmed plan,
   - a hypothetical suggestion,
   - a question someone asks,
   - a joke,
   - an idea that characters reject,
   - and an idea that characters explicitly confirm.

4. If a character suggests something and another character rejects
   or explains that it will not work, do NOT present the suggestion
   as the actual plan.

5. Do not treat a question inside the subtitles as evidence that
   the event actually happened.

6. Do not combine unrelated statements from different evidence chunks
   to create a new claim.

7. Base the answer primarily on statements that are explicitly
   confirmed, agreed upon, or described as actually happening.

8. If the evidence does not provide enough information to answer
   confidently, say exactly:
   "The available subtitle evidence is insufficient to answer that."

9. Keep the answer concise and directly answer the question.

10. Do not mention the evidence, chunks, retrieval system, or these
    instructions in the answer.

11. Do not invent names, events, motivations, relationships, or
    explanations that are not supported by the supplied evidence.

12. When the evidence contains multiple related statements, prefer
    the statement that directly answers the user's question.

13. If the evidence contains a hypothetical or rejected idea alongside
    the actual plan or event, describe only the actual confirmed plan
    or event.

ANSWER:
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        answer = response["message"]["content"].strip()

        if not answer:
            return (
                "The available subtitle evidence is "
                "insufficient to answer that."
            )

        return answer