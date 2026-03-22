from app.services.summarizer import generate_summary


def test_generate_summary_returns_text_and_keywords() -> None:
    text = """
    Contrato de prestación de servicios para emisión de carta fianza.
    El contratante solicita el servicio con vigencia de 30 días calendario.
    El contratista entregará la documentación requerida.
    El contrato incluye condiciones, vigencia y firma de las partes.
    """

    result = generate_summary(text)

    assert result["short_summary"]
    assert result["keywords"] is not None
    assert "contrato" in str(result["keywords"])