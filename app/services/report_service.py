from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from app.config.app_config import RUNTIME_REPORT_FILE
from app.utils.runtime_paths import get_runtime_file_path


@dataclass
class ProcessedItem:
    collaborator_key: str
    message: str
    generated_count: int = 0


@dataclass
class SkippedItem:
    collaborator_key: str
    reason: str


@dataclass
class ErrorItem:
    collaborator_key: str
    reason: str


@dataclass
class ExecutionReport:
    mode: str
    selected_pdf_count: int
    identified_group_count: int = 0
    processed_items: list[ProcessedItem] = field(default_factory=list)
    skipped_items: list[SkippedItem] = field(default_factory=list)
    error_items: list[ErrorItem] = field(default_factory=list)

    def build_text(self) -> str:
        now_text = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        lines = [
            "RELATORIO DE PROCESSAMENTO",
            "",
            f"Modo: {self.mode}",
            f"Data/Hora: {now_text}",
            f"Total de PDFs selecionados: {self.selected_pdf_count}",
            f"Total de grupos identificados: {self.identified_group_count}",
            "",
            "RESUMO",
            f"- Processados com sucesso: {len(self.processed_items)}",
            f"- Nao processados: {len(self.skipped_items)}",
            f"- Erros de execucao: {len(self.error_items)}",
            "",
            "PROCESSADOS COM SUCESSO",
        ]

        if self.processed_items:
            for item in self.processed_items:
                lines.append(
                    f"- {item.collaborator_key} -> {item.generated_count} arquivos gerados"
                )
        else:
            lines.append("- Nenhum")

        lines.append("")
        lines.append("NAO PROCESSADOS")

        if self.skipped_items:
            for item in self.skipped_items:
                lines.append(f"- {item.collaborator_key} -> {item.reason}")
        else:
            lines.append("- Nenhum")

        lines.append("")
        lines.append("ERROS DE EXECUCAO")

        if self.error_items:
            for item in self.error_items:
                lines.append(f"- {item.collaborator_key} -> {item.reason}")
        else:
            lines.append("- Nenhum")

        lines.append("")
        return "\n".join(lines)


def get_runtime_report_path() -> Path:
    return get_runtime_file_path(RUNTIME_REPORT_FILE)


def save_execution_report(report: ExecutionReport) -> Path:
    report_path = get_runtime_report_path()
    report_path.write_text(report.build_text(), encoding="utf-8")
    return report_path