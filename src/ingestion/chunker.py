def time_to_seconds(timestamp: str) -> float:
    """Convert HH:MM:SS,mmm into seconds."""

    hours, minutes, seconds = timestamp.split(":")
    seconds, milliseconds = seconds.split(",")

    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(milliseconds) / 1000
    )


def create_chunks(
    entries: list[dict],
    max_duration: float = 60.0,
    overlap_duration: float = 7.0,
) -> list[dict]:
    """
    Create contextual chunks from cleaned subtitle entries.

    Chunks do not exceed the maximum duration under normal
    subtitle-entry boundaries. Overlap is created using
    complete subtitle entries to preserve dialogue context.
    """

    if not entries:
        return []

    chunks = []
    current_entries = []
    chunk_start = None

    for entry in entries:
        entry_start = time_to_seconds(entry["start_time"])
        entry_end = time_to_seconds(entry["end_time"])

        # Start the first chunk.
        if not current_entries:
            current_entries = [entry]
            chunk_start = entry_start
            continue

        current_duration = entry_end - chunk_start

        # Add the subtitle while staying within the maximum duration.
        if current_duration <= max_duration:
            current_entries.append(entry)
            continue

        # The next subtitle would exceed max_duration,
        # so finalize the current chunk.
        chunks.append(
            build_chunk(
                current_entries,
                len(chunks) + 1,
            )
        )

        # Determine which recent subtitle entries should be
        # carried into the next chunk for contextual overlap.
        overlap_start = entry_start - overlap_duration

        overlap_entries = [
            previous
            for previous in current_entries
            if time_to_seconds(previous["end_time"]) >= overlap_start
        ]

        # Start the next chunk with the overlapping entries
        # followed by the subtitle that caused the boundary.
        current_entries = overlap_entries + [entry]

        # Make sure the overlap does not cause the new chunk
        # to exceed the maximum duration.
        while (
            len(current_entries) > 1
            and (
                entry_end
                - time_to_seconds(current_entries[0]["start_time"])
                > max_duration
            )
        ):
            current_entries.pop(0)

        chunk_start = time_to_seconds(
            current_entries[0]["start_time"]
        )

    # Add the final chunk.
    if current_entries:
        chunks.append(
            build_chunk(
                current_entries,
                len(chunks) + 1,
            )
        )

    return chunks


def build_chunk(entries: list[dict], chunk_number: int) -> dict:
    """Build a single contextual chunk from subtitle entries."""

    first = entries[0]
    last = entries[-1]

    return {
        "chunk_id": f"{first['movie']}_{chunk_number:04d}",
        "movie": first["movie"],
        "start_time": first["start_time"],
        "end_time": last["end_time"],
        "text": "\n".join(
            entry["text"]
            for entry in entries
        ),
        "subtitle_ids": [
            entry["subtitle_id"]
            for entry in entries
        ],
    }