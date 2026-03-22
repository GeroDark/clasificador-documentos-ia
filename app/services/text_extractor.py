from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


def extract_text_from_txt(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8", errors="ignore").strip()


def extract_text_from_docx(file_path: str) -> str:
    document = DocxDocument(file_path)
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs).strip()


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    parts: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            parts.append(text.strip())

    return "\n".join(parts).strip()


def extract_text_by_extension(file_path: str, extension: str) -> str:
    extension = extension.lower()

    if extension == ".txt":
        return extract_text_from_txt(file_path)

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    raise ValueError("Tipo de archivo no soportado para extracción de texto.")