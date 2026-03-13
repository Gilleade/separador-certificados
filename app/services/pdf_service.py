import fitz


def get_pdf_page_count(pdf_path: str) -> int:
    doc = fitz.open(pdf_path)
    try:
        return doc.page_count
    finally:
        doc.close()


def export_pages_to_pdf(source_pdf_path: str, pages: list[int], output_pdf_path: str) -> None:
    source_doc = fitz.open(source_pdf_path)
    output_doc = fitz.open()

    try:
        for page_number in pages:
            page_index = page_number - 1

            if page_index < 0 or page_index >= source_doc.page_count:
                raise ValueError(
                    f"A página {page_number} não existe no arquivo '{source_pdf_path}'."
                )

            output_doc.insert_pdf(source_doc, from_page=page_index, to_page=page_index)

        output_doc.save(output_pdf_path, garbage=4, deflate=True)
    finally:
        output_doc.close()
        source_doc.close()