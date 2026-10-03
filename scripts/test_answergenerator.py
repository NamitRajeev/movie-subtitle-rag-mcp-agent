from src.retrieval.retriever import Retriever
from src.generation.answer_generator import AnswerGenerator


question = "What does Thanos want from the Avengers?"

movie = (
    "Avengers.Infinity.War.2018."
    "1080p.BluRay.x265-YAWNTiC_eng"
)


# Retrieve relevant subtitle evidence
retriever = Retriever()

evidence = retriever.retrieve(
    question,
    n_results=5,
    movie=movie,
)


# Generate an answer from the evidence
generator = AnswerGenerator()

answer = generator.generate(
    question,
    evidence,
)


print("\nQuestion:")
print(question)

print("\nAnswer:")
print(answer)