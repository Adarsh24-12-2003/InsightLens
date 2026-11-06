
"""Create the configured InsightLens RAG pipeline."""

from pathlib import Path

from dotenv import load_dotenv

from src.ingestion.ingest_all import index_all_records
from src.retrieval.embeddings import EmbeddingService
from src.retrieval.llm import LLMService
from src.retrieval.rag_pipeline import RAGPipeline
from src.retrieval.retriever import Retriever
from src.retrieval.vector_store import VectorStore


def create_pipeline() -> RAGPipeline:
    """Build and return the fully configured RAG pipeline."""

    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")

    collection_name = "insightlens_multimodal"
    persist_directory = str(
        project_root / "data" / "processed" / "chroma_db"
    )

    vector_store = VectorStore(
        collection_name=collection_name,
        persist_directory=persist_directory,
    )

    collection = vector_store.get_collection()

    # Automatically ingest data if the database is empty.
    if collection.count() == 0:
        vector_store = index_all_records(
            collection_name=collection_name
        )
        collection = vector_store.get_collection()

    embedding_service = EmbeddingService()

    retriever = Retriever(
        collection=collection,
        embedding_service=embedding_service,
    )

    llm = LLMService()

    return RAGPipeline(
        retriever=retriever,
        llm=llm,
    )
