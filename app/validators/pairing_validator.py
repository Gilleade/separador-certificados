from dataclasses import dataclass
from typing import List, Optional

from app.services.file_identification_service import (
    IdentifiedPdfFile,
    find_file_by_type,
)


@dataclass
class PairingValidationResult:
    is_valid: bool
    message: str
    nrs_file: Optional[IdentifiedPdfFile] = None
    nr37_file: Optional[IdentifiedPdfFile] = None
    person_name_base: str = ""
    person_name_output: str = ""


def validate_selected_pdf_pair(
    identified_files: List[IdentifiedPdfFile],
) -> PairingValidationResult:
    """
    Valida o conjunto de arquivos selecionados pelo usuário.

    Regras da versão 1:
    - devem existir exatamente 2 arquivos
    - deve existir 1 arquivo NRS
    - deve existir 1 arquivo NR37
    - ambos devem pertencer ao mesmo colaborador
    """
    if not identified_files:
        return PairingValidationResult(
            is_valid=False,
            message="Nenhum arquivo foi selecionado.",
        )

    if len(identified_files) != 2:
        return PairingValidationResult(
            is_valid=False,
            message="Selecione exatamente 2 arquivos PDF: 1 NRS e 1 NR-37.",
        )

    unidentified_files = [
        item.original_filename
        for item in identified_files
        if item.certificate_type is None
    ]
    if unidentified_files:
        joined_names = ", ".join(unidentified_files)
        return PairingValidationResult(
            is_valid=False,
            message=(
                "Não foi possível identificar o tipo de um ou mais arquivos: "
                f"{joined_names}. Verifique se os nomes contêm 'NRS' e 'NR-37'."
            ),
        )

    nrs_files = [item for item in identified_files if item.certificate_type == "NRS"]
    nr37_files = [item for item in identified_files if item.certificate_type == "NR37"]

    if len(nrs_files) != 1 or len(nr37_files) != 1:
        return PairingValidationResult(
            is_valid=False,
            message="A seleção deve conter exatamente 1 arquivo NRS e 1 arquivo NR-37.",
        )

    nrs_file = find_file_by_type(identified_files, "NRS")
    nr37_file = find_file_by_type(identified_files, "NR37")

    if nrs_file is None or nr37_file is None:
        return PairingValidationResult(
            is_valid=False,
            message="Falha interna ao organizar os arquivos identificados.",
        )

    if not nrs_file.person_name_base or not nr37_file.person_name_base:
        return PairingValidationResult(
            is_valid=False,
            message="Não foi possível extrair o nome do colaborador dos arquivos selecionados.",
        )

    if nrs_file.person_name_base != nr37_file.person_name_base:
        return PairingValidationResult(
            is_valid=False,
            message=(
                "Os arquivos selecionados parecem pertencer a colaboradores diferentes: "
                f"'{nrs_file.person_name_base}' e '{nr37_file.person_name_base}'."
            ),
        )

    return PairingValidationResult(
        is_valid=True,
        message="Arquivos validados com sucesso.",
        nrs_file=nrs_file,
        nr37_file=nr37_file,
        person_name_base=nrs_file.person_name_base,
        person_name_output=nrs_file.person_name_output,
    )