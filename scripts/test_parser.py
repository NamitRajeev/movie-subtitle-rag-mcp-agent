from src.ingestion.parser import parse_srt

file_path = "data/subtitles/Avengers.Infinity.War.2018.1080p.BluRay.x265-YAWNTiC_eng.srt"

entries = parse_srt(file_path)

print(f"Total subtitle entries: {len(entries)}")

print("\nFirst subtitle:")
print(entries[0])

print("\nLast subtitle:")
print(entries[-1])