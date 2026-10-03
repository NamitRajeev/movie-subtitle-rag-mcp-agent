def build_citations(evidence: list[dict]) -> list[str]:
    """
    Build deterministic movie and timestamp citations
    from retrieved evidence.
    """

    citations = []

    for item in evidence:
        citation = (
            f"[{item['movie']} — "
            f"{item['start_time']} -> "
            f"{item['end_time']}]"
        )

        if citation not in citations:
            citations.append(citation)

    return citations