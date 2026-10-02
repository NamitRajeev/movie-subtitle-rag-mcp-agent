import re


def clean_subtitle_text(text: str) -> str:
    """
    Clean subtitle text while preserving useful scene context.
    """

    # Remove HTML/XML-style formatting tags such as <i>, </i>, <b>, etc.
    text = re.sub(r"<[^>]+>", "", text)

    # Replace multiple whitespace characters with a single space
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def clean_entries(entries: list[dict]) -> list[dict]:
    """
    Clean the text field of parsed subtitle entries.
    """

    cleaned_entries = []

    for entry in entries:
        cleaned_text = clean_subtitle_text(entry["text"])

        # Skip entries that become empty after cleaning
        if not cleaned_text:
            continue

        cleaned_entry = entry.copy()
        cleaned_entry["text"] = cleaned_text

        cleaned_entries.append(cleaned_entry)

    return cleaned_entries