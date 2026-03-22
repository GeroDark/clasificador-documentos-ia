import re


def clean_value(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" :.-\n\t")


def extract_company(text: str) -> str | None:
    patterns = [
        r"(?:empresa|raz[oó]n social)\s*:\s*([^\n\r]+)",
        r"(?:señores|señor)\s*:\s*([^\n\r]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return clean_value(match.group(1))
    return None


def extract_amount(text: str) -> str | None:
    patterns = [
        r"(S\/\s*[\d\.,]+)",
        r"(\$\s*[\d\.,]+)",
        r"(?:monto referencial|importe total|monto a pagar|total)\s*:\s*([^\n\r]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return clean_value(match.group(1))
    return None


def extract_date(text: str) -> str | None:
    patterns = [
        r"\b(\d{2}/\d{2}/\d{4})\b",
        r"\b(\d{4}-\d{2}-\d{2})\b",
        r"\b(\d{1,2}\s+de\s+[a-záéíóúñ]+\s+de\s+\d{4})\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return clean_value(match.group(1))
    return None


def extract_subject(text: str) -> str | None:
    pattern = r"(?:asunto)\s*:\s*([^\n\r]+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match:
        return clean_value(match.group(1))
    return None


def extract_validity(text: str) -> str | None:
    patterns = [
        r"(?:vigencia)\s*:\s*([^\n\r]+)",
        r"(\d+\s+d[ií]as?\s+calendario)",
        r"(\d+\s+d[ií]as?\s+h[aá]biles)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return clean_value(match.group(1))
    return None


def extract_sender(text: str) -> str | None:
    patterns = [
        r"(?:remitente)\s*:\s*([^\n\r]+)",
        r"(?:atentamente[,:\s]+)([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ\s\.]{3,})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return clean_value(match.group(1))
    return None


def extract_fields(text: str) -> list[dict[str, str | float]]:
    fields: list[dict[str, str | float]] = []

    mapping = {
        "company_name": extract_company(text),
        "amount": extract_amount(text),
        "date": extract_date(text),
        "subject": extract_subject(text),
        "validity": extract_validity(text),
        "sender": extract_sender(text),
    }

    for field_name, field_value in mapping.items():
        if field_value:
            fields.append(
                {
                    "field_name": field_name,
                    "field_value": str(field_value),
                    "confidence": 0.8,
                    "method": "rules",
                }
            )

    return fields