from app.services.classifier import classify_text


def test_classify_contract_text() -> None:
    text = """
    Contrato de prestación de servicios.
    Las partes acuerdan la siguiente cláusula de vigencia.
    El contratante y el contratista firman el presente documento.
    """

    result = classify_text(text)

    assert result["category"] == "contract"
    assert float(result["confidence"]) > 0


def test_classify_proposal_text() -> None:
    text = """
    Propuesta comercial para servicio de emisión de carta fianza.
    Incluye alcance del servicio y oferta económica.
    """

    result = classify_text(text)

    assert result["category"] == "proposal"