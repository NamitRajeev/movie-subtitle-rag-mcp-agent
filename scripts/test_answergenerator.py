from src.retrieval.retriever import Retriever
from src.generation.answer_generator import AnswerGenerator
from src.retrieval.citations import build_citations


question = "What does Thanos want from the Avengers?"

movie = (
    "Avengers.Infinity.War.2018."
    "1080p.BluRay.x265-YAWNTiC_eng"
)


retriever = Retriever()

evidence = retriever.retrieve(
    question,
    n_results=5,
    movie=movie,
)


print("\nRetrieved Evidence:")
print("=" * 60)

for i, item in enumerate(evidence, start=1):
    print(f"\nEvidence {i}")
    print(
        f"Time: {item['start_time']} -> "
        f"{item['end_time']}"
    )
    print(f"Distance: {item['score']:.4f}")
    print(item["text"])


generator = AnswerGenerator()

answer = generator.generate(
    question,
    evidence,
)


citations = build_citations(evidence)


print("\n\nAnswer:")
print("=" * 60)
print(answer)

print("\nSources:")
for citation in citations:
    print(citation)