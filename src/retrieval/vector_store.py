from pathlib import Path

import chromadb


class VectorStore:
    """Manage document storage and similarity search using ChromaDB."""

    def __init__(
        self,
        collection_name: str = "insightlens_multimodal",
        persist_directory: str = "data/processed/chroma_db",
    ):
        self.persist_directory = str(Path(persist_directory).resolve())
        self.client = chromadb.PersistentClient(path=self.persist_directory)

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(
        self,
        documents: list,
        embeddings: list,
        metadatas: list,
        ids: list,
    ) -> None:
        """Store documents, embeddings and metadata in ChromaDB."""

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def add_records(self, records: list[dict]) -> None:
        """Store already structured ingestion records in ChromaDB."""
        if not records:
            return

        self.collection.upsert(
            ids=[record["id"] for record in records],
            documents=[record["text"] for record in records],
            metadatas=[record["metadata"] for record in records],
        )

    def get_collection(self):
        """Return the ChromaDB collection."""
        return self.collection