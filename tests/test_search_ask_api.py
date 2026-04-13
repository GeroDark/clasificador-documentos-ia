from types import SimpleNamespace

from app.models.query_log import QueryLog


def test_semantic_search_returns_mocked_results(client, monkeypatch, auth_headers) -> None:
    monkeypatch.setattr("app.api.routes.search.embed_query", lambda text: [0.1, 0.2, 0.3])
    monkeypatch.setattr(
        "app.api.routes.search.fetch_semantic_search_rows",
        lambda db, query_embedding, limit: [
            (
                SimpleNamespace(id=10, chunk_index=0, chunk_text="Primer fragmento relevante."),
                SimpleNamespace(id=1, original_filename="contrato-a.pdf"),
                0.08,
            ),
            (
                SimpleNamespace(id=11, chunk_index=1, chunk_text="Segundo fragmento relevante."),
                SimpleNamespace(id=2, original_filename="contrato-b.pdf"),
                0.24,
            ),
        ],
    )

    response = client.get(
        "/api/search/semantic/",
        params={"q": "monto contrato", "limit": 2},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "document_id": 1,
            "document_filename": "contrato-a.pdf",
            "chunk_id": 10,
            "chunk_index": 0,
            "chunk_text": "Primer fragmento relevante.",
            "score": 0.92,
        },
        {
            "document_id": 2,
            "document_filename": "contrato-b.pdf",
            "chunk_id": 11,
            "chunk_index": 1,
            "chunk_text": "Segundo fragmento relevante.",
            "score": 0.76,
        },
    ]


def test_semantic_search_returns_empty_list_when_no_results(client, monkeypatch, auth_headers) -> None:
    monkeypatch.setattr("app.api.routes.search.embed_query", lambda text: [0.1, 0.2, 0.3])
    monkeypatch.setattr(
        "app.api.routes.search.fetch_semantic_search_rows",
        lambda db, query_embedding, limit: [],
    )

    response = client.get(
        "/api/search/semantic/",
        params={"q": "consulta valida"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_semantic_search_validates_short_query(client, auth_headers) -> None:
    response = client.get("/api/search/semantic/", params={"q": "a"}, headers=auth_headers)

    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == "validation_error"
    assert payload["message"] == "La solicitud no cumple el contrato esperado."


def test_ask_returns_mocked_answer_and_sources(
    client, db_session, monkeypatch, auth_headers
) -> None:
    monkeypatch.setattr("app.api.routes.ask.embed_query", lambda text: [0.5, 0.1, 0.9])
    monkeypatch.setattr(
        "app.api.routes.ask.fetch_ask_rows",
        lambda db, query_embedding, limit, document_id=None: [
            (
                SimpleNamespace(id=21, chunk_index=0, chunk_text="Monto referencial: S/ 53,200.00."),
                SimpleNamespace(id=7, original_filename="propuesta.pdf"),
                0.03,
            )
        ],
    )
    monkeypatch.setattr(
        "app.api.routes.ask.answer_question",
        lambda question, sources: {
            "answer": "Monto referencial: S/ 53,200.00.",
            "confidence": 0.97,
        },
    )

    response = client.post(
        "/api/ask/",
        json={"question": "¿Cuál es el monto referencial?", "document_id": 7, "top_k": 3},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "question": "¿Cuál es el monto referencial?",
        "answer": "Monto referencial: S/ 53,200.00.",
        "confidence": 0.97,
        "document_id": 7,
        "sources": [
            {
                "chunk_id": 21,
                "document_id": 7,
                "document_filename": "propuesta.pdf",
                "chunk_index": 0,
                "chunk_text": "Monto referencial: S/ 53,200.00.",
                "score": 0.97,
            }
        ],
    }

    stored_logs = db_session.query(QueryLog).all()
    assert len(stored_logs) == 1
    assert stored_logs[0].question == "¿Cuál es el monto referencial?"
    assert stored_logs[0].document_id == 7


def test_ask_returns_not_found_when_no_relevant_chunks_exist(
    client, monkeypatch, auth_headers
) -> None:
    monkeypatch.setattr("app.api.routes.ask.embed_query", lambda text: [0.5, 0.1, 0.9])
    monkeypatch.setattr(
        "app.api.routes.ask.fetch_ask_rows",
        lambda db, query_embedding, limit, document_id=None: [],
    )

    response = client.post(
        "/api/ask/",
        json={"question": "¿Cuál es el monto referencial?", "document_id": 999},
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "not_found",
        "message": "No se encontraron fragmentos relevantes para responder.",
        "details": None,
    }


def test_ask_validates_short_question(client, auth_headers) -> None:
    response = client.post("/api/ask/", json={"question": "a"}, headers=auth_headers)

    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == "validation_error"
    assert payload["message"] == "La solicitud no cumple el contrato esperado."
