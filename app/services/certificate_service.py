from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from app.config.certificate_rules import CERTIFICATE_RULES, EXPECTED_PAGE_COUNTS
from app.services.pdf_service import export_pages_to_pdf, get_pdf_page_count


@dataclass
class GenerationResult:
    success: bool
    message: str
    generated_files: list[str] = field(default_factory=list)


def _log(log_callback: Optional[Callable[[str], None]], message: str) -> None:
    if log_callback:
        log_callback(message)


def ensure_unique_output_path(output_folder: str, filename: str) -> Path:
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    candidate = output_dir / filename
    if not candidate.exists():
        return candidate

    base_name = candidate.stem
    extension = candidate.suffix
    counter = 2

    while True:
        new_candidate = output_dir / f"{base_name}_{counter}{extension}"
        if not new_candidate.exists():
            return new_candidate
        counter += 1


def validate_expected_page_count(pdf_path: str, expected_count: int, label: str) -> None:
    current_count = get_pdf_page_count(pdf_path)

    if current_count != expected_count:
        raise ValueError(
            f"O arquivo {label} deveria ter {expected_count} páginas, mas possui {current_count}."
        )


def _generate_group(
    source_pdf_path: str,
    group_name: str,
    person_name_output: str,
    output_folder: str,
    generated_files: list[str],
) -> None:
    rules = CERTIFICATE_RULES[group_name]

    for rule in rules:
        output_filename = f"{person_name_output}_{rule['suffix']}.pdf"
        output_path = ensure_unique_output_path(output_folder, output_filename)

        export_pages_to_pdf(source_pdf_path, rule["pages"], str(output_path))
        generated_files.append(str(output_path))


def generate_certificates(
    nrs_pdf_path: str,
    nr37_pdf_path: str,
    person_name_output: str,
    output_folder: str,
    log_callback: Optional[Callable[[str], None]] = None,
) -> GenerationResult:
    safe_person_name = person_name_output.strip() or "COLABORADOR"
    generated_files: list[str] = []

    _log(log_callback, "Validando os arquivos selecionados...")

    validate_expected_page_count(
        nrs_pdf_path,
        EXPECTED_PAGE_COUNTS["NRS"],
        "NRS",
    )
    validate_expected_page_count(
        nr37_pdf_path,
        EXPECTED_PAGE_COUNTS["NR37"],
        "NR-37",
    )

    _log(log_callback, "Gerando certificados do arquivo NRS...")
    _generate_group(
        source_pdf_path=nrs_pdf_path,
        group_name="NRS",
        person_name_output=safe_person_name,
        output_folder=output_folder,
        generated_files=generated_files,
    )

    _log(log_callback, "Gerando certificados do arquivo NR-37...")
    _generate_group(
        source_pdf_path=nr37_pdf_path,
        group_name="NR37",
        person_name_output=safe_person_name,
        output_folder=output_folder,
        generated_files=generated_files,
    )

    _log(log_callback, f"Total de arquivos gerados: {len(generated_files)}")

    return GenerationResult(
        success=True,
        message=f"Processamento concluído com sucesso. {len(generated_files)} arquivos foram gerados.",
        generated_files=generated_files,
    )