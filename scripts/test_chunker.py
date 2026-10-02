from src.ingestion.parser import parse_srt
from src.ingestion.cleaner import clean_entries
from src.ingestion.chunker import create_chunks


file_path = (
    "data/subtitles/"
    "Avengers.Infinity.War.2018.1080p.BluRay.x265-YAWNTiC_eng.srt"
)


# 1. Parse
entries = parse_srt(file_path)

# 2. Clean
cleaned_entries = clean_entries(entries)

# 3. Create chunks
chunks = create_chunks(cleaned_entries)


print(f"Subtitle entries: {len(cleaned_entries)}")
print(f"Chunks created: {len(chunks)}")


# --------------------------------------------------
# First chunk
# --------------------------------------------------

print("\nFirst chunk:")
print("=" * 60)

print(f"Chunk ID: {chunks[0]['chunk_id']}")
print(f"Movie: {chunks[0]['movie']}")
print(
    f"Time: {chunks[0]['start_time']} "
    f"-> {chunks[0]['end_time']}"
)
print(f"Subtitle IDs: {chunks[0]['subtitle_ids']}")

print("\nDialogue:")
print(chunks[0]["text"])


# --------------------------------------------------
# Last chunk
# --------------------------------------------------

print("\nLast chunk:")
print("=" * 60)

print(f"Chunk ID: {chunks[-1]['chunk_id']}")
print(f"Movie: {chunks[-1]['movie']}")
print(
    f"Time: {chunks[-1]['start_time']} "
    f"-> {chunks[-1]['end_time']}"
)
print(f"Subtitle IDs: {chunks[-1]['subtitle_ids']}")


# --------------------------------------------------
# Boundary / overlap check
# --------------------------------------------------

print("\nChunk boundary check:")
print("=" * 60)

for i in range(min(3, len(chunks) - 1)):
    current = chunks[i]
    next_chunk = chunks[i + 1]

    print(f"\nChunk {i + 1}:")
    print(
        f"{current['start_time']} "
        f"-> {current['end_time']}"
    )

    print(f"Chunk {i + 2}:")
    print(
        f"{next_chunk['start_time']} "
        f"-> {next_chunk['end_time']}"
    )

    overlap_ids = set(
        current["subtitle_ids"]
    ) & set(
        next_chunk["subtitle_ids"]
    )

    print(
        f"Overlapping subtitle IDs: "
        f"{sorted(overlap_ids)}"
    )