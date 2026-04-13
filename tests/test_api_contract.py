def test_job_not_found_returns_standard_error_contract(client) -> None:
    response = client.get("/api/jobs/999/status")

    assert response.status_code == 404
    assert response.json() == {
        "code": "not_found",
        "message": "Job no encontrado.",
        "details": None,
    }


def test_invalid_upload_returns_standard_error_contract(client) -> None:
    response = client.post(
        "/api/documents/upload/",
        files={"file": ("malicioso.exe", b"binario", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "bad_request",
        "message": "Tipo de archivo no permitido. Solo se aceptan PDF, DOCX y TXT.",
        "details": None,
    }


def test_validation_errors_follow_standard_contract(client) -> None:
    response = client.get("/api/search/semantic/", params={"q": "a"})

    assert response.status_code == 422
    payload = response.json()

    assert payload["code"] == "validation_error"
    assert payload["message"] == "La solicitud no cumple el contrato esperado."
    assert isinstance(payload["details"], list)
    assert payload["details"][0]["type"] == "string_too_short"


def test_openapi_documents_upload_documents_error_schema(client) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    upload_operation = payload["paths"]["/api/documents/upload/"]["post"]

    assert upload_operation["summary"] == "Subir documento y encolar procesamiento"
    assert (
        upload_operation["responses"]["400"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/ApiErrorResponse"
    )
