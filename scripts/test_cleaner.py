from src.ingestion.parser import parse_srt
from src.ingestion.cleaner import clean_entries


file_path = "data/subtitles/Avengers.Infinity.War.2018.1080p.BluRay.x265-YAWNTiC_eng.srt"

entries = parse_srt(file_path)

print(f"Parsed subtitle entries: {len(entries)}")

print("\nBefore cleaning:")
print(entries[0])

cleaned_entries = clean_entries(entries)

print("\nAfter cleaning:")
print(cleaned_entries[0])

print(f"\nCleaned subtitle entries: {len(cleaned_entries)}")