from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from app.services.batch_grouping_service import BatchGroup, group_pdf_files_for_batch
from app.services.certificate_service import generate_certificates
from app.services.report_service import (
    ErrorItem,
    ExecutionReport,
    ProcessedItem,
    SkippedItem,
    save_execution_report,
)


@dataclass
class BatchProcessingResult:
    success: bool
    message: str
    report_path: str
    processed_count: int
    skipped_count: int
    error_count: int


def _log(log_callback: Optional[Callable[[str], None]], message: str) -> None:
    if log_callback:
        log_callback(message)


def _get_group_skip_reason(group: BatchGroup) -> Optional[str]:
    if len(group.nrs_files) == 0:
        return "faltando arquivo NRS"

    if len(group.nr37_files) == 0:
        return "faltando arquivo NR-37"

    if len(group.nrs_files) > 1:
        return "duplicidade de arquivo NRS"

    if len(group.nr37_files) > 1:
        return "duplicidade de arquivo NR-37"

    return None


def process_batch_files(
    file_paths: list[str],
    output_root_folder: str,
    log_callback: Optional[Callable[[str], None]] = None,
) -> BatchProcessingResult:
    grouping_result = group_pdf_files_for_batch(file_paths)

    report = ExecutionReport(
        mode="Lote",
        selected_pdf_count=len(file_paths),
        identified_group_count=len(grouping_result.groups),
    )

    output_root = Path(output_root_folder)
    output_root.mkdir(parents=True, exist_ok=True)

    if grouping_result.unidentified_files:
        for item in grouping_result.unidentified_files:
            report.skipped_items.append(
                SkippedItem(
                    collaborator_key=item.original_filename,
                    reason="tipo do arquivo nao identificado",
                )
            )

    for group in grouping_result.groups.values():
        skip_reason = _get_group_skip_reason(group)

        if skip_reason:
            report.skipped_items.append(
                SkippedItem(
                    collaborator_key=group.display_name,
                    reason=skip_reason,
                )
            )
            _log(log_callback, f"{group.display_name}: nao processado ({skip_reason}).")
            continue

        try:
            collaborator_output_folder = output_root / group.collaborator_key
            collaborator_output_folder.mkdir(parents=True, exist_ok=True)

            _log(log_callback, f"Processando {group.display_name}...")

            generation_result = generate_certificates(
                nrs_pdf_path=group.nrs_files[0].original_path,
                nr37_pdf_path=group.nr37_files[0].original_path,
                person_name_output=group.output_name,
                output_folder=str(collaborator_output_folder),
                log_callback=None,
            )

            report.processed_items.append(
                ProcessedItem(
                    collaborator_key=group.display_name,
                    message="processado com sucesso",
                    generated_count=len(generation_result.generated_files),
                )
            )

            _log(
                log_callback,
                f"{group.display_name}: {len(generation_result.generated_files)} arquivos gerados.",
            )

        except Exception as error:
            report.error_items.append(
                ErrorItem(
                    collaborator_key=group.display_name,
                    reason=str(error),
                )
            )
            _log(log_callback, f"{group.display_name}: erro no processamento.")

    report_path = save_execution_report(report)

    processed_count = len(report.processed_items)
    skipped_count = len(report.skipped_items)
    error_count = len(report.error_items)

    message = (
        f"Lote concluido. "
        f"Processados: {processed_count} | "
        f"Nao processados: {skipped_count} | "
        f"Erros: {error_count}"
    )

    _log(log_callback, message)
    _log(log_callback, f"Relatorio atualizado em: {report_path}")

    return BatchProcessingResult(
        success=True,
        message=message,
        report_path=str(report_path),
        processed_count=processed_count,
        skipped_count=skipped_count,
        error_count=error_count,
    )