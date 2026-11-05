"""Extract text and metadata from the business report PDF."""

from __future__ import annotations

from pathlib import Path

import fitz


def process_pdf(pdf_path: str | Path) -> list[dict]:
    """Return PDF text chunks with page metadata for retrieval indexing."""
    pdf_path = Path(pdf_path)
    doc = fitz.open(pdf_path)

    records: list[dict] = []
    for page_index in range(doc.page_count):
        page = doc[page_index]
        text = page.get_text("text")
        cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())

        if not cleaned:
            continue

        chunk_text = (
            "source_type=pdf; source_name="
            f"{pdf_path.name}; page={page_index + 1}; "
            f"section='report'; content='{cleaned}'"
        )

        metadata = {
            "source_filename": pdf_path.name,
            "source_name": pdf_path.name,
            "source_type": "pdf",
            "modality": "text",
            "document_type": "report_page",
            "page_number": page_index + 1,
            "page": page_index + 1,
            "original_file": str(pdf_path),
            "section": "report",
        }

        records.append(
            {
                "id": f"pdf_{pdf_path.stem}_{page_index + 1}",
                "text": chunk_text,
                "metadata": metadata,
            }
        )

    return records
