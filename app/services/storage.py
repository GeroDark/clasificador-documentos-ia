from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings


def save_upload_file(upload_file: UploadFile) -> tuple[str, str]:
    settings = get_settings()
    uploads_dir = Path(settings.uploads_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    original_name = upload_file.filename or "archivo_sin_nombre"
    extension = Path(original_name).suffix.lower()
    generated_name = f"{uuid4().hex}{extension}"
    destination = uploads_dir / generated_name

    with destination.open("wb") as buffer:
        content = upload_file.file.read()
        buffer.write(content)

    return generated_name, str(destination)