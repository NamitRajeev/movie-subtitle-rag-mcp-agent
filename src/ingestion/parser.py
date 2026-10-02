from pathlib import Path
import pysrt


def parse_srt(file_path: str) -> list[dict]:
    """
    Parse an SRT file into structured subtitle entries.

    Each subtitle entry contains:
    - movie
    - subtitle_id
    - start_time
    - end_time
    - text
    """

    path = Path(file_path)

    # Movie name comes from the filename
    movie = path.stem

    # Load the SRT file
    # utf-8-sig removes a UTF-8 BOM if the file contains one
    subtitles = pysrt.open(str(path), encoding="utf-8-sig")

    entries = []

    for subtitle in subtitles:
        text = subtitle.text.strip()

        # Ignore completely empty subtitle entries
        if not text:
            continue

        entry = {
            "movie": movie,
            "subtitle_id": subtitle.index,
            "start_time": str(subtitle.start),
            "end_time": str(subtitle.end),
            "text": text,
        }

        entries.append(entry)

    return entries