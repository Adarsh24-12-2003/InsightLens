import chromadb


class VectorStore:
    """Manage document storage and similarity search using ChromaDB."""

    def __init__(
        self,
        collection_name: str = "insightlens",
        persist_directory: str = "chroma_db",
    ):
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

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

    def get_collection(self):
        """Return the ChromaDB collection."""
        return self.collection