import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from app.utils.text_utils import (
    normalize_input_filename,
    normalize_person_name_for_output,
    normalize_spaces,
)


@dataclass
class IdentifiedPdfFile:
    original_path: str
    original_filename: str
    normalized_filename: str
    certificate_type: Optional[str]
    person_name_base: str
    person_name_output: str


def detect_certificate_type(normalized_filename: str) -> Optional[str]:
    """
    Detecta o tipo do arquivo a partir do nome já normalizado.

    Retornos possíveis:
    - "NRS"
    - "NR37"
    - None
    """
    if re.search(r"\bNRS\b", normalized_filename):
        return "NRS"

    if re.search(r"\bNR-37\b", normalized_filename):
        return "NR37"

    return None


def extract_person_name_base(normalized_filename: str, certificate_type: Optional[str]) -> str:
    """
    Remove o trecho do tipo do certificado do nome normalizado
    e devolve apenas o nome-base do colaborador.
    """
    if not normalized_filename:
        return ""

    result = normalized_filename

    if certificate_type == "NRS":
        result = re.sub(r"\bNRS\b", "", result)

    elif certificate_type == "NR37":
        result = re.sub(r"\bNR-37\b", "", result)

    result = normalize_spaces(result)
    return result


def identify_pdf_file(file_path: str) -> IdentifiedPdfFile:
    """
    Identifica um único arquivo PDF.
    """
    path = Path(file_path)
    original_filename = path.name

    normalized_filename = normalize_input_filename(original_filename)
    certificate_type = detect_certificate_type(normalized_filename)
    person_name_base = extract_person_name_base(normalized_filename, certificate_type)
    person_name_output = normalize_person_name_for_output(person_name_base)

    return IdentifiedPdfFile(
        original_path=str(path),
        original_filename=original_filename,
        normalized_filename=normalized_filename,
        certificate_type=certificate_type,
        person_name_base=person_name_base,
        person_name_output=person_name_output,
    )


def identify_pdf_files(file_paths: List[str]) -> List[IdentifiedPdfFile]:
    """
    Identifica uma lista de arquivos PDF.
    """
    return [identify_pdf_file(file_path) for file_path in file_paths]


def find_file_by_type(
    identified_files: List[IdentifiedPdfFile],
    certificate_type: str
) -> Optional[IdentifiedPdfFile]:
    """
    Retorna o primeiro arquivo do tipo informado.
    Exemplo de tipos:
    - "NRS"
    - "NR37"
    """
    for item in identified_files:
        if item.certificate_type == certificate_type:
            return item
    return None