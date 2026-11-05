"""Build and index the complete multimodal dataset for retrieval."""

from __future__ import annotations

from pathlib import Path

from src.ingestion.chart_processor import process_chart
from src.ingestion.csv_processor import process_csv
from src.ingestion.pdf_processor import process_pdf
from src.ingestion.transcript_processor import process_transcript
from src.retrieval.embeddings import EmbeddingService
from src.retrieval.vector_store import VectorStore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def build_all_records() -> list[dict]:
    """Process all raw dataset files into standardized retrieval records."""
    records: list[dict] = []

    records.extend(process_pdf(DATA_DIR / "G3_business_report.pdf"))
    records.extend(process_chart(DATA_DIR / "G3_revenue_chart.png", DATA_DIR / "G3_sales_ground_truth.csv"))
    records.extend(process_chart(DATA_DIR / "G3_profit_chart.png", DATA_DIR / "G3_sales_ground_truth.csv"))
    records.extend(process_transcript(DATA_DIR / "G3_video_transcript.json"))
    records.extend(process_csv(DATA_DIR / "G3_sales_ground_truth.csv"))

    return records


def index_all_records(collection_name: str = "insightlens_multimodal") -> VectorStore:
    """Embed the processed records and store them in ChromaDB."""
    records = build_all_records()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    embedding_service = EmbeddingService()
    vector_store = VectorStore(
        collection_name=collection_name,
        persist_directory=str(PROCESSED_DIR / "chroma_db"),
    )

    embeddings = embedding_service.embed_documents([record["text"] for record in records])
    vector_store.collection.upsert(
        ids=[record["id"] for record in records],
        documents=[record["text"] for record in records],
        embeddings=embeddings,
        metadatas=[record["metadata"] for record in records],
    )

    return vector_store


if __name__ == "__main__":
    vector_store = index_all_records()
    print(f"Indexed {vector_store.collection.count()} records in {vector_store.persist_directory}")
