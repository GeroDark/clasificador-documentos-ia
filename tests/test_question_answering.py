from app.services.question_answering import answer_question


def test_answer_question_returns_amount_sentence() -> None:
    question = "¿Cuál es el monto referencial?"
    sources = [
        {
            "chunk_text": (
                "Carta de presentación de propuesta comercial. "
                "Monto referencial: S/ 53,200.00. "
                "Vigencia: 30 días calendario."
            ),
            "score": 0.91,
            "chunk_id": 1,
            "document_id": 1,
            "document_filename": "propuesta.txt",
            "chunk_index": 0,
        }
    ]

    result = answer_question(question, sources)

    assert "53,200.00" in str(result["answer"])
    assert float(result["confidence"]) > 0