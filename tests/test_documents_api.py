from types import SimpleNamespace

from app.models.document import Document


def test_upload_document_creates_document_and_job(client, db_session, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.routes.documents.save_upload_file",
        lambda upload_file: ("stored-propuesta.txt", "uploads/stored-propuesta.txt"),
    )
    monkeypatch.setattr(
        "app.api.routes.documents.process_document_task.delay",
        lambda document_id, job_id: SimpleNamespace(id=f"task-{document_id}-{job_id}"),
    )

    response = client.post(
        "/api/documents/upload/",
        files={"file": ("propuesta.txt", b"contenido de prueba", "text/plain")},
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "queued"
    assert payload["task_id"] == f"task-{payload['document_id']}-{payload['id']}"

    document = db_session.get(Document, payload["document_id"])
    assert document is not None
    assert document.original_filename == "propuesta.txt"
    assert document.stored_filename == "stored-propuesta.txt"
    assert document.file_path == "uploads/stored-propuesta.txt"
    assert document.status == "queued"


def test_upload_document_rejects_unsupported_extension(client) -> None:
    response = client.post(
        "/api/documents/upload/",
        files={"file": ("malicioso.exe", b"binario", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Tipo de archivo no permitido. Solo se aceptan PDF, DOCX y TXT."
    )


def test_list_documents_returns_persisted_documents(client, document_factory) -> None:
    first = document_factory(original_filename="a.txt", status="metadata_only")
    second = document_factory(original_filename="b.pdf", status="indexed")

    response = client.get("/api/documents/")

    assert response.status_code == 200
    payload = response.json()
    returned_ids = {item["id"] for item in payload}

    assert returned_ids == {first.id, second.id}
    assert {item["original_filename"] for item in payload} == {"a.txt", "b.pdf"}
