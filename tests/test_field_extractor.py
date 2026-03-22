from app.services.field_extractor import extract_fields


def test_extract_fields_returns_expected_values() -> None:
    text = """
    Carta de presentación de propuesta comercial.
    Empresa: CIE Consultora Empresarial
    Asunto: Servicio de emisión de carta fianza
    Monto referencial: S/ 53,200.00
    Vigencia: 30 días calendario
    Fecha: 21/03/2026
    Remitente: José Ricardo Soberón Cruzado
    """

    result = extract_fields(text)

    result_map = {item["field_name"]: item["field_value"] for item in result}

    assert result_map["company_name"] == "CIE Consultora Empresarial"
    assert result_map["subject"] == "Servicio de emisión de carta fianza"
    assert result_map["amount"] == "S/ 53,200.00"
    assert result_map["validity"] == "30 días calendario"
    assert result_map["date"] == "21/03/2026"