def clean_text_start(text: str) -> str:
    """Remove leading stop words and capitalize the first meaningful word."""
    stop_words = {"and", "or", "but", "so", "because", "of", "to", "in", "on", "for", "with", "at", "by", "from"}
    words = text.strip().split()

    # Remove all leading stop words
    while words and words[0].lower() in stop_words:
        words.pop(0)

    if not words:
        return ""

    # Capitalize only the first meaningful word
    words[0] = words[0][0].upper() + words[0][1:]
    return " ".join(words)
