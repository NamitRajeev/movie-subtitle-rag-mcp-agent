# evaluation/run_evaluation.py

import asyncio
import json

import ollama

from src.agent.agent import MovieAgent
from src.agent.schemas import AgentRequest
from src.retrieval.vector_store import VectorStore


EVALUATION_FILE = "evaluation/questions.json"
RESULTS_FILE = "evaluation/results.json"
JUDGE_MODEL = "qwen2.5:3b"


def load_questions():
    with open(
        EVALUATION_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def get_movie_mapping():
    vector_store = VectorStore()
    movies = vector_store.get_movies()

    return {
        movie.lower(): movie
        for movie in movies
    }


def resolve_movie(
    movie_name,
    movie_mapping,
):
    if movie_name is None:
        return None

    normalized = movie_name.lower().strip()

    if normalized in movie_mapping:
        return movie_mapping[normalized]

    matches = [
        actual_movie
        for actual_movie in movie_mapping.values()
        if normalized in actual_movie.lower()
    ]

    if len(matches) == 1:
        return matches[0]

    return movie_name


def evaluate_behavior(
    expected_behavior,
    actual_status,
    answer,
):
    if expected_behavior == "answer":
        return actual_status == "success"

    if expected_behavior == "abstain":
        if actual_status != "success":
            return False

        if not answer:
            return False

        normalized_answer = answer.lower()

        abstention_phrases = [
            "insufficient to answer",
            "not enough information",
            "cannot answer",
            "can't answer",
            "unable to answer",
            "not sufficient evidence",
        ]

        return any(
            phrase in normalized_answer
            for phrase in abstention_phrases
        )

    if expected_behavior == "movie_not_found":
        return actual_status == "not_found"

    if expected_behavior == "clarification":
        return actual_status == "clarification"

    return False


def evaluate_case(
    agent,
    case,
    movie_mapping,
):
    movie = resolve_movie(
        case["movie"],
        movie_mapping,
    )

    request = AgentRequest(
        intent="information",
        movie=movie,
        query=case["question"],
    )

    result = asyncio.run(
        agent.process(request)
    )

    expected_behavior = case[
        "expected_behavior"
    ]

    actual_status = result.get(
        "status"
    )

    answer = result.get(
        "answer"
    )

    behavior_correct = evaluate_behavior(
        expected_behavior,
        actual_status,
        answer,
    )

    return {
        "id": case["id"],
        "movie": movie,
        "question": case["question"],
        "category": case["category"],
        "expected_behavior": expected_behavior,
        "actual_status": actual_status,
        "behavior_correct": behavior_correct,
        "answer": answer,
        "citations": result.get(
            "citations",
            [],
        ),
        "evidence": result.get(
            "evidence",
            [],
        ),
    }


def build_evidence_text(
    evidence,
):
    if not evidence:
        return (
            "No subtitle evidence was retrieved."
        )

    parts = []

    for index, item in enumerate(
        evidence,
        start=1,
    ):
        parts.append(
            f"""
Evidence {index}
Movie: {item.get("movie")}
Timestamp: {item.get("start_time")} -> {item.get("end_time")}
Subtitle text:
{item.get("text")}
"""
        )

    return "\n".join(parts)


def clean_json_response(
    content,
):
    content = content.strip()

    if content.startswith("```"):
        lines = content.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    return content


def judge_answer(
    result,
):
    answer = result.get(
        "answer"
    )

    # There is no generated answer to judge
    # for cases such as clarification or movie not found.
    if not answer:
        return {
            "answer_correct": None,
            "grounded": None,
            "unsupported_claims": None,
            "reason": (
                "No generated answer to evaluate."
            ),
        }

    question = result[
        "question"
    ]

    evidence_text = build_evidence_text(
        result.get(
            "evidence",
            [],
        )
    )

    prompt = f"""
You are evaluating a movie subtitle RAG system.

Evaluate the generated answer ONLY against the supplied
subtitle evidence.

Do NOT use your general knowledge about the movie.

QUESTION:
{question}

GENERATED ANSWER:
{answer}

RETRIEVED SUBTITLE EVIDENCE:
{evidence_text}

Evaluate the answer using these rules:

1. answer_correct:
   True only if the answer directly and accurately answers
   the question using the supplied evidence.

2. grounded:
   True only if the important claims in the answer are
   explicitly supported by the supplied subtitle evidence.

3. unsupported_claims:
   True if the answer contains any important claim that is
   not supported by the supplied subtitle evidence.

4. If the evidence is insufficient and the answer correctly
   states that the evidence is insufficient, mark:
   answer_correct = true
   grounded = true
   unsupported_claims = false.

5. Do not penalize concise answers for omitting unnecessary
   details.

6. Do not use outside knowledge about the movie.

7. Do not assume that a suggestion, question, hypothetical,
   rejected idea, or joke actually happened.

8. If the evidence contains conflicting statements, prefer
   explicit confirmation over speculation or rejected ideas.

9. If the answer adds names, events, motivations, relationships,
   or explanations that are not present in the evidence,
   mark unsupported_claims = true.

10. The answer must be supported by the retrieved evidence,
    not merely by the judge's knowledge of the movie.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "answer_correct": true,
    "grounded": true,
    "unsupported_claims": false,
    "reason": "Short explanation based only on the supplied evidence."
}}
"""

    try:
        response = ollama.chat(
            model=JUDGE_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        content = response[
            "message"
        ][
            "content"
        ].strip()

        content = clean_json_response(
            content
        )

        judgment = json.loads(
            content
        )

        if not isinstance(
            judgment,
            dict,
        ):
            raise ValueError(
                "Judge response was not a JSON object."
            )

        return {
            "answer_correct": bool(
                judgment.get(
                    "answer_correct",
                    False,
                )
            ),
            "grounded": bool(
                judgment.get(
                    "grounded",
                    False,
                )
            ),
            "unsupported_claims": bool(
                judgment.get(
                    "unsupported_claims",
                    True,
                )
            ),
            "reason": judgment.get(
                "reason",
                "No reason provided.",
            ),
        }

    except Exception as error:
        return {
            "answer_correct": None,
            "grounded": None,
            "unsupported_claims": None,
            "reason": (
                f"Judge failed: "
                f"{type(error).__name__}: {error}"
            ),
        }


def print_case_result(
    result,
):
    print(
        "\n" + "-" * 70
    )

    print(
        f"CASE {result['id']}: "
        f"{result['question']}"
    )

    print(
        "-" * 70
    )

    print(
        f"Behavior: "
        f"{'PASS' if result['behavior_correct'] else 'FAIL'}"
    )

    print(
        f"Status: "
        f"{result['actual_status']}"
    )

    if result.get("answer"):
        print(
            f"Answer: "
            f"{result['answer']}"
        )

    if "answer_correct" in result:

        print(
            f"Answer correctness: "
            f"{result['answer_correct']}"
        )

        print(
            f"Grounded: "
            f"{result['grounded']}"
        )

        print(
            f"Unsupported claims: "
            f"{result['unsupported_claims']}"
        )

        print(
            f"Judge: "
            f"{result['judge_reason']}"
        )

    print(
        f"Citations: "
        f"{len(result.get('citations', []))}"
    )


def print_summary(
    results,
):
    total = len(results)

    behavior_passed = sum(
        result["behavior_correct"]
        for result in results
    )

    judged_results = [
        result
        for result in results
        if result.get(
            "answer_correct"
        ) is not None
    ]

    answer_correct = sum(
        result["answer_correct"]
        for result in judged_results
    )

    grounded = sum(
        result["grounded"]
        for result in judged_results
    )

    unsupported = sum(
        result["unsupported_claims"]
        for result in judged_results
    )

    print("\n")
    print(
        "=" * 70
    )
    print(
        "EVALUATION SUMMARY"
    )
    print(
        "=" * 70
    )

    print(
        f"Total cases: "
        f"{total}"
    )

    print(
        f"Behavior correctness: "
        f"{behavior_passed}/{total} "
        f"("
        f"{behavior_passed / total * 100:.1f}"
        f"%)"
    )

    if judged_results:

        judged_total = len(
            judged_results
        )

        print(
            f"Answer correctness: "
            f"{answer_correct}/"
            f"{judged_total} "
            f"("
            f"{answer_correct / judged_total * 100:.1f}"
            f"%)"
        )

        print(
            f"Grounded answers: "
            f"{grounded}/"
            f"{judged_total} "
            f"("
            f"{grounded / judged_total * 100:.1f}"
            f"%)"
        )

        print(
            f"Answers with unsupported claims: "
            f"{unsupported}/"
            f"{judged_total} "
            f"("
            f"{unsupported / judged_total * 100:.1f}"
            f"%)"
        )

    else:

        print(
            "Answer correctness: "
            "No answers were judged."
        )


def main():
    questions = load_questions()
    movie_mapping = get_movie_mapping()

    print(
        "=" * 70
    )
    print(
        "MOVIE RAG AUTOMATIC EVALUATION"
    )
    print(
        "=" * 70
    )

    print(
        "\nIndexed movies:"
    )

    for movie in movie_mapping.values():
        print(
            f"- {movie}"
        )

    print(
        f"\nEvaluation cases: "
        f"{len(questions)}"
    )

    agent = MovieAgent()
    results = []

    for case in questions:

        print(
            f"\n[{case['id']}/"
            f"{len(questions)}] "
            f"{case['question']}"
        )

        result = evaluate_case(
            agent,
            case,
            movie_mapping,
        )

        judgment = judge_answer(
            result
        )

        result["answer_correct"] = (
            judgment["answer_correct"]
        )

        result["grounded"] = (
            judgment["grounded"]
        )

        result["unsupported_claims"] = (
            judgment["unsupported_claims"]
        )

        result["judge_reason"] = (
            judgment["reason"]
        )

        results.append(
            result
        )

        print_case_result(
            result
        )

    print_summary(
        results
    )

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"\nDetailed results saved to:"
        f"\n{RESULTS_FILE}"
    )


if __name__ == "__main__":
    main()