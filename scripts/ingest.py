from pathlib import Path

from src.ingestion.parser import parse_srt
from src.ingestion.cleaner import clean_entries
from src.ingestion.chunker import create_chunks
from src.retrieval.embedding import EmbeddingModel
from src.retrieval.vector_store import VectorStore


SUBTITLE_DIRECTORY = Path("data/subtitles")


def main():
    # Find all SRT files
    subtitle_files = sorted(
        SUBTITLE_DIRECTORY.glob("*.srt")
    )

    if not subtitle_files:
        print("No SRT files found.")
        return

    print(f"Found {len(subtitle_files)} subtitle files.")

    # Initialize models and vector store once
    embedding_model = EmbeddingModel()
    vector_store = VectorStore()

    total_entries = 0
    total_chunks = 0

    for file_path in subtitle_files:

        print("\n" + "=" * 60)
        print(f"Processing: {file_path.name}")
        print("=" * 60)

        # Parse
        entries = parse_srt(str(file_path))

        # Clean
        cleaned_entries = clean_entries(entries)

        # Create contextual chunks
        chunks = create_chunks(cleaned_entries)

        # Create embeddings
        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = embedding_model.encode(texts)

        # Store in ChromaDB
        vector_store.add_chunks(
            chunks,
            embeddings,
        )

        total_entries += len(cleaned_entries)
        total_chunks += len(chunks)

        print(f"Subtitle entries: {len(cleaned_entries)}")
        print(f"Chunks created: {len(chunks)}")
        print(f"Chunks stored.")


    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)

    print(f"Movies processed: {len(subtitle_files)}")
    print(f"Total subtitle entries: {total_entries}")
    print(f"Total chunks created: {total_chunks}")
    print(f"Total chunks in ChromaDB: {vector_store.count()}")


if __name__ == "__main__":
    main()