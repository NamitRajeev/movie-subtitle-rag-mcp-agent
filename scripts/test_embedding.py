from src.ingestion.parser import parse_srt
from src.ingestion.cleaner import clean_entries
from src.ingestion.chunker import create_chunks
from src.retrieval.embedding import EmbeddingModel


file_path = (
    "data/subtitles/"
    "Avengers.Infinity.War.2018.1080p.BluRay.x265-YAWNTiC_eng.srt"
)


# Parse
entries = parse_srt(file_path)

# Clean
cleaned_entries = clean_entries(entries)

# Create contextual chunks
chunks = create_chunks(cleaned_entries)

print(f"Chunks: {len(chunks)}")


# Create embedding model
embedding_model = EmbeddingModel()


# Embed the first 3 chunks
texts = [
    chunk["text"]
    for chunk in chunks[:3]
]

embeddings = embedding_model.encode(texts)


print(f"Number of embeddings: {len(embeddings)}")
print(f"Embedding dimension: {len(embeddings[0])}")

print("\nFirst embedding:")
print(embeddings[0][:10])