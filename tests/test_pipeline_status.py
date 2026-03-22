def test_processing_status_values() -> None:
    allowed = {"queued", "processing", "completed", "failed"}
    assert "queued" in allowed
    assert "processing" in allowed
    assert "completed" in allowed
    assert "failed" in allowed