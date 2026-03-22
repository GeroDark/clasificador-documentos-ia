import re
from collections import Counter


STOPWORDS = {
    "de", "la", "el", "los", "las", "y", "a", "en", "por", "para", "con", "del",
    "al", "un", "una", "que", "se", "su", "sus", "o", "u", "es", "son", "como",
    "más", "mas", "sobre", "entre", "sin", "este", "esta", "estos", "estas",
    "documento", "documentos", "cuál", "cual", "qué", "que", "quién", "quien",
}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"\b[\wáéíóúñü]{2,}\b", text.lower())
    return [word for word in words if word not in STOPWORDS]


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[\.\!\?])\s+|\n+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def _question_intents(question: str) -> set[str]:
    q = question.lower()
    intents: set[str] = set()

    if any(word in q for word in ["monto", "importe", "total", "pagar", "precio"]):
        intents.add("amount")
    if any(word in q for word in ["fecha", "cuándo", "cuando"]):
        intents.add("date")
    if any(word in q for word in ["vigencia", "vence", "vencimiento", "duración", "duracion"]):
        intents.add("validity")
    if any(word in q for word in ["asunto", "tema", "objeto"]):
        intents.add("subject")
    if any(word in q for word in ["empresa", "razón social", "razon social", "cliente"]):
        intents.add("company")
    if any(word in q for word in ["remitente", "firma", "firmó", "firmo"]):
        intents.add("sender")

    return intents


def _bonus_for_sentence(sentence: str, intents: set[str]) -> int:
    s = sentence.lower()
    bonus = 0

    if "amount" in intents and (re.search(r"(s\/|\$)\s*[\d\.,]+", s) or "monto" in s or "importe" in s):
        bonus += 2
    if "date" in intents and (
        re.search(r"\b\d{2}/\d{2}/\d{4}\b", s)
        or re.search(r"\b\d{4}-\d{2}-\d{2}\b", s)
        or "fecha" in s
    ):
        bonus += 2
    if "validity" in intents and ("vigencia" in s or "vencimiento" in s or "días" in s or "dias" in s):
        bonus += 2
    if "subject" in intents and ("asunto" in s or "objeto" in s):
        bonus += 2
    if "company" in intents and ("empresa" in s or "razón social" in s or "razon social" in s):
        bonus += 2
    if "sender" in intents and ("remitente" in s or "atentamente" in s or "firma" in s):
        bonus += 2

    return bonus


def answer_question(
    question: str,
    sources: list[dict[str, str | int | float]],
) -> dict[str, str | float]:
    question_tokens = tokenize(question)
    question_counts = Counter(question_tokens)
    intents = _question_intents(question)

    sentence_candidates: list[tuple[str, float, int]] = []

    for source in sources:
        chunk_text = str(source["chunk_text"])
        source_score = float(source["score"])
        sentences = split_sentences(chunk_text)

        for sentence in sentences:
            sentence_tokens = tokenize(sentence)
            overlap = sum(question_counts[token] for token in sentence_tokens if token in question_counts)
            bonus = _bonus_for_sentence(sentence, intents)
            final_score = overlap + bonus + source_score
            sentence_candidates.append((sentence, source_score, int(final_score * 1000)))

    if not sentence_candidates:
        return {
            "answer": "No se encontró información suficiente para responder la pregunta.",
            "confidence": 0.0,
        }

    ranked = sorted(sentence_candidates, key=lambda item: item[2], reverse=True)
    best_sentence, best_source_score, best_rank = ranked[0]

    if best_rank <= 0:
        fallback = ranked[0][0]
        return {
            "answer": fallback,
            "confidence": round(min(0.3, best_source_score), 2),
        }

    selected_sentences = []
    seen = set()
    for sentence, _, _ in ranked:
        normalized = sentence.strip().lower()
        if normalized not in seen:
            selected_sentences.append(sentence.strip())
            seen.add(normalized)
        if len(selected_sentences) == 2:
            break

    answer = " ".join(selected_sentences).strip()
    confidence = round(min(1.0, (best_rank / 10) + best_source_score / 2), 2)

    return {
        "answer": answer,
        "confidence": confidence,
    }