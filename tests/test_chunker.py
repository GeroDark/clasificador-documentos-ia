from app.services.chunker import split_into_chunks


def test_split_into_chunks_returns_multiple_chunks_for_long_text() -> None:
    text = (
        "Primer párrafo del documento. " * 20
        + "\n\n"
        + "Segundo párrafo del documento. " * 20
    )

    chunks = split_into_chunks(text, max_chars=150, overlap=20)

    assert len(chunks) >= 2
    assert all(chunk.strip() for chunk in chunks)