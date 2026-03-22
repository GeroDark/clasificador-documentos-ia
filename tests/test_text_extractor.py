from pathlib import Path

from app.services.text_extractor import extract_text_from_txt


def test_extract_text_from_txt(tmp_path: Path) -> None:
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("Hola mundo", encoding="utf-8")

    extracted = extract_text_from_txt(str(sample_file))

    assert extracted == "Hola mundo"