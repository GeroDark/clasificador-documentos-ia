def test_get_job_status_returns_existing_job(client, job_factory, auth_headers) -> None:
    job = job_factory(status="processing", task_id="task-running")

    response = client.get(f"/api/jobs/{job.id}/status", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == job.id
    assert payload["document_id"] == job.document_id
    assert payload["status"] == "processing"
    assert payload["task_id"] == "task-running"


def test_get_job_status_returns_404_for_missing_job(client, auth_headers) -> None:
    response = client.get("/api/jobs/999/status", headers=auth_headers)

    assert response.status_code == 404
    assert response.json() == {
        "code": "not_found",
        "message": "Job no encontrado.",
        "details": None,
    }
