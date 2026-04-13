import re
from collections import defaultdict

CATEGORY_RULES: dict[str, list[str]] = {
    "contract": [
        r"\bcontrato\b",
        r"\bacuerdo\b",
        r"\bcl[aá]usula\b",
        r"\bpartes\b",
        r"\bvigencia\b",
        r"\bfirmado\b",
        r"\bcontratante\b",
        r"\bcontratista\b",
    ],
    "proposal": [
        r"\bpropuesta\b",
        r"\bcotizaci[oó]n\b",
        r"\boferta econ[oó]mica\b",
        r"\bpropuesta comercial\b",
        r"\balcance\b",
        r"\bservicio ofrecido\b",
    ],
    "invoice": [
        r"\bfactura\b",
        r"\bruc\b",
        r"\bsubtotal\b",
        r"\bigv\b",
        r"\bimporte total\b",
        r"\bmonto a pagar\b",
        r"\bcomprobante\b",
    ],
    "letter": [
        r"\bcarta\b",
        r"\bde nuestra consideraci[oó]n\b",
        r"\bseñores\b",
        r"\basunto\b",
        r"\batentamente\b",
        r"\bpresente\b",
    ],
    "report": [
        r"\binforme\b",
        r"\bconclusiones\b",
        r"\brecomendaciones\b",
        r"\bantecedentes\b",
        r"\ban[aá]lisis\b",
        r"\bresultados\b",
    ],
}


def normalize_text(text: str) -> str:
    return text.lower().strip()


def classify_text(text: str) -> dict[str, str | float]:
    normalized = normalize_text(text)
    scores: dict[str, int] = defaultdict(int)
    matched: dict[str, list[str]] = defaultdict(list)

    for category, patterns in CATEGORY_RULES.items():
        for pattern in patterns:
            if re.search(pattern, normalized, flags=re.IGNORECASE):
                scores[category] += 1
                matched[category].append(pattern)

    if not scores:
        return {
            "category": "other",
            "confidence": 0.0,
            "method": "rules",
            "matched_keywords": None,
        }

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]
    total_patterns = len(CATEGORY_RULES[best_category])
    confidence = round(best_score / total_patterns, 2)

    return {
        "category": best_category,
        "confidence": confidence,
        "method": "rules",
        "matched_keywords": ", ".join(matched[best_category]) if matched[best_category] else None,
    }