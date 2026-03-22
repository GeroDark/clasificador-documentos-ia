import re


def split_into_chunks(text: str, max_chars: int = 700, overlap: int = 120) -> list[str]:
    text = text.strip()
    if not text:
        return []

    paragraphs = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if not current:
                current = sentence
                continue

            candidate = f"{current} {sentence}".strip()
            if len(candidate) <= max_chars:
                current = candidate
            else:
                chunks.append(current)
                tail = current[-overlap:] if overlap and len(current) > overlap else ""
                current = f"{tail} {sentence}".strip()

    if current:
        chunks.append(current)

    return [chunk.strip() for chunk in chunks if chunk.strip()]