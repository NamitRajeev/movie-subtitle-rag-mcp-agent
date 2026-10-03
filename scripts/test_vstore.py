from src.ingestion.parser import parse_srt
from src.ingestion.cleaner import clean_entries
from src.ingestion.chunker import create_chunks
from src.retrieval.embedding import EmbeddingModel
from src.retrieval.vector_store import VectorStore


file_path = (
    "data/subtitles/"
    "Avengers.Infinity.War.2018.1080p.BluRay.x265-YAWNTiC_eng.srt"
)


# Parse

entries = parse_srt(file_path)


# Clean

cleaned_entries = clean_entries(entries)

# Create chunks

chunks = create_chunks(cleaned_entries)

print(f"Chunks: {len(chunks)}")



# Create embeddings


embedding_model = EmbeddingModel()

texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = embedding_model.encode(texts)

print(f"Embeddings: {len(embeddings)}")
print(f"Embedding dimension: {len(embeddings[0])}")



# Create vector store

vector_store = VectorStore()

vector_store.add_chunks(
    chunks,
    embeddings,
)


# Verify storage

print(f"Chunks stored: {vector_store.count()}")