import re
from collections import Counter

STOPWORDS = {
    "de", "la", "el", "los", "las", "y", "a", "en", "por", "para", "con", "del",
    "al", "un", "una", "que", "se", "su", "sus", "o", "u", "es", "son", "como",
    "más", "mas", "sobre", "entre", "sin", "este", "esta", "estos", "estas",
    "documento", "presente", "servicio",
}


def split_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[\.\!\?])\s+|\n+", text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def tokenize(text: str) -> list[str]:
    words = re.findall(r"\b[\wáéíóúñü]{3,}\b", text.lower())
    return [word for word in words if word not in STOPWORDS]


def generate_summary(text: str) -> dict[str, str | None]:
    sentences = split_sentences(text)
    if not sentences:
        return {
            "short_summary": "",
            "key_points": None,
            "keywords": None,
            "method": "extractive_rules",
        }

    tokens = tokenize(text)
    if not tokens:
        short_summary = " ".join(sentences[:2]).strip()
        return {
            "short_summary": short_summary,
            "key_points": short_summary,
            "keywords": None,
            "method": "extractive_rules",
        }

    frequencies = Counter(tokens)
    scored_sentences: list[tuple[str, int]] = []

    for sentence in sentences:
        sentence_tokens = tokenize(sentence)
        score = sum(frequencies[token] for token in sentence_tokens)
        scored_sentences.append((sentence, score))

    top_sentences = sorted(scored_sentences, key=lambda item: item[1], reverse=True)[:3]
    ordered_top_sentences = [sentence for sentence, _ in top_sentences if sentence]

    short_summary = " ".join(ordered_top_sentences[:2]).strip()
    key_points = "\n".join(f"- {sentence}" for sentence in ordered_top_sentences[:3]).strip()
    keywords = ", ".join(word for word, _ in frequencies.most_common(8))

    return {
        "short_summary": short_summary,
        "key_points": key_points or None,
        "keywords": keywords or None,
        "method": "extractive_rules",
    }