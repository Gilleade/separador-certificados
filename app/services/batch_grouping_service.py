from dataclasses import dataclass, field
from pathlib import Path

from app.services.file_identification_service import IdentifiedPdfFile, identify_pdf_files


@dataclass
class BatchGroup:
    collaborator_key: str
    display_name: str
    output_name: str
    nrs_files: list[IdentifiedPdfFile] = field(default_factory=list)
    nr37_files: list[IdentifiedPdfFile] = field(default_factory=list)


@dataclass
class BatchGroupingResult:
    identified_files: list[IdentifiedPdfFile]
    valid_identified_files: list[IdentifiedPdfFile]
    unidentified_files: list[IdentifiedPdfFile]
    groups: dict[str, BatchGroup]


def build_collaborator_key(identified_file: IdentifiedPdfFile) -> str:
    return identified_file.person_name_output.strip()


def build_output_short_name(identified_file: IdentifiedPdfFile) -> str:
    parts = [part for part in identified_file.person_name_output.split("_") if part]

    if not parts:
        return "COLABORADOR"

    if len(parts) == 1:
        return parts[0]

    return f"{parts[0]}_{parts[-1]}"


def group_pdf_files_for_batch(file_paths: list[str]) -> BatchGroupingResult:
    identified_files = identify_pdf_files(file_paths)

    valid_identified_files: list[IdentifiedPdfFile] = []
    unidentified_files: list[IdentifiedPdfFile] = []
    groups: dict[str, BatchGroup] = {}

    for identified_file in identified_files:
        if identified_file.certificate_type not in {"NRS", "NR37"}:
            unidentified_files.append(identified_file)
            continue

        valid_identified_files.append(identified_file)

        collaborator_key = build_collaborator_key(identified_file)
        display_name = identified_file.person_name_base or Path(identified_file.original_path).stem
        output_name = build_output_short_name(identified_file)

        if collaborator_key not in groups:
            groups[collaborator_key] = BatchGroup(
                collaborator_key=collaborator_key,
                display_name=display_name,
                output_name=output_name,
            )

        group = groups[collaborator_key]

        if identified_file.certificate_type == "NRS":
            group.nrs_files.append(identified_file)
        elif identified_file.certificate_type == "NR37":
            group.nr37_files.append(identified_file)

    return BatchGroupingResult(
        identified_files=identified_files,
        valid_identified_files=valid_identified_files,
        unidentified_files=unidentified_files,
        groups=groups,
    )