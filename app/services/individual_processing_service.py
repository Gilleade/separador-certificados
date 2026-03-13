from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from app.services.file_identification_service import identify_pdf_files
from app.services.certificate_service import (
    _generate_group,
    validate_expected_page_count,
)
from app.services.report_service import (
    ErrorItem,
    ExecutionReport,
    ProcessedItem,
    SkippedItem,
    save_execution_report,
)


@dataclass
class IndividualProcessingResult:
    success: bool
    message: str
    report_path: str
    generated_count: int


def _log(log_callback: Optional[Callable[[str], None]], message: str) -> None:
    if log_callback:
        log_callback(message)


def process_individual_files(
    file_paths: list[str],
    output_folder: str,
    log_callback: Optional[Callable[[str], None]] = None,
) -> IndividualProcessingResult:
    report = ExecutionReport(
        mode="Individual",
        selected_pdf_count=len(file_paths),
        identified_group_count=1 if file_paths else 0,
    )

    if not file_paths:
        report.skipped_items.append(
            SkippedItem(
                collaborator_key="SELECAO",
                reason="nenhum arquivo foi selecionado",
            )
        )
        report_path = save_execution_report(report)
        return IndividualProcessingResult(
            success=False,
            message="Nenhum arquivo foi selecionado.",
            report_path=str(report_path),
            generated_count=0,
        )

    identified_files = identify_pdf_files(file_paths)

    unidentified_files = [item for item in identified_files if item.certificate_type is None]
    if unidentified_files:
        for item in unidentified_files:
            report.skipped_items.append(
                SkippedItem(
                    collaborator_key=item.original_filename,
                    reason="tipo do arquivo nao identificado",
                )
            )

        report_path = save_execution_report(report)
        return IndividualProcessingResult(
            success=False,
            message="Ha arquivos que nao puderam ser identificados.",
            report_path=str(report_path),
            generated_count=0,
        )

    nrs_files = [item for item in identified_files if item.certificate_type == "NRS"]
    nr37_files = [item for item in identified_files if item.certificate_type == "NR37"]

    if len(nrs_files) > 1:
        report.skipped_items.append(
            SkippedItem(
                collaborator_key=nrs_files[0].person_name_base or "COLABORADOR",
                reason="duplicidade de arquivo NRS",
            )
        )
        report_path = save_execution_report(report)
        return IndividualProcessingResult(
            success=False,
            message="Existe mais de um arquivo NRS selecionado.",
            report_path=str(report_path),
            generated_count=0,
        )

    if len(nr37_files) > 1:
        report.skipped_items.append(
            SkippedItem(
                collaborator_key=nr37_files[0].person_name_base or "COLABORADOR",
                reason="duplicidade de arquivo NR-37",
            )
        )
        report_path = save_execution_report(report)
        return IndividualProcessingResult(
            success=False,
            message="Existe mais de um arquivo NR-37 selecionado.",
            report_path=str(report_path),
            generated_count=0,
        )

    if len(nrs_files) == 0 and len(nr37_files) == 0:
        report.skipped_items.append(
            SkippedItem(
                collaborator_key="COLABORADOR",
                reason="nenhum arquivo valido foi encontrado",
            )
        )
        report_path = save_execution_report(report)
        return IndividualProcessingResult(
            success=False,
            message="Nenhum arquivo valido foi encontrado.",
            report_path=str(report_path),
            generated_count=0,
        )

    detected_names = {
        item.person_name_output
        for item in identified_files
        if item.person_name_output.strip()
    }

    if len(detected_names) > 1:
        report.skipped_items.append(
            SkippedItem(
                collaborator_key="SELECAO",
                reason="os arquivos selecionados parecem pertencer a colaboradores diferentes",
            )
        )
        report_path = save_execution_report(report)
        return IndividualProcessingResult(
            success=False,
            message="Os arquivos selecionados parecem pertencer a colaboradores diferentes.",
            report_path=str(report_path),
            generated_count=0,
        )

    reference_file = nrs_files[0] if nrs_files else nr37_files[0]
    collaborator_display_name = reference_file.person_name_base or "COLABORADOR"
    collaborator_output_name = reference_file.person_name_output or "COLABORADOR"

    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_count = 0

    try:
        if len(nrs_files) == 1:
            _log(log_callback, f"Gerando certificados NRS para {collaborator_display_name}...")
            validate_expected_page_count(nrs_files[0].original_path, 26, "NRS")

            generated_files_nrs: list[str] = []
            _generate_group(
                source_pdf_path=nrs_files[0].original_path,
                group_name="NRS",
                person_name_output=collaborator_output_name,
                output_folder=str(output_dir),
                generated_files=generated_files_nrs,
            )
            generated_count += len(generated_files_nrs)

        if len(nr37_files) == 1:
            _log(log_callback, f"Gerando certificados NR-37 para {collaborator_display_name}...")
            validate_expected_page_count(nr37_files[0].original_path, 8, "NR-37")

            generated_files_nr37: list[str] = []
            _generate_group(
                source_pdf_path=nr37_files[0].original_path,
                group_name="NR37",
                person_name_output=collaborator_output_name,
                output_folder=str(output_dir),
                generated_files=generated_files_nr37,
            )
            generated_count += len(generated_files_nr37)

        report.processed_items.append(
            ProcessedItem(
                collaborator_key=collaborator_display_name,
                message="processado com sucesso",
                generated_count=generated_count,
            )
        )

        report_path = save_execution_report(report)

        return IndividualProcessingResult(
            success=True,
            message=f"Processamento individual concluido. {generated_count} arquivos gerados.",
            report_path=str(report_path),
            generated_count=generated_count,
        )

    except Exception as error:
        report.error_items.append(
            ErrorItem(
                collaborator_key=collaborator_display_name,
                reason=str(error),
            )
        )
        report_path = save_execution_report(report)

        return IndividualProcessingResult(
            success=False,
            message=str(error),
            report_path=str(report_path),
            generated_count=generated_count,
        )