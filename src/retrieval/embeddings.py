from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Generate text embeddings using Sentence Transformers."""

    def __init__(self):
        """Initialize the embedding service."""
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def embed_text(self, text: str) -> list:
        """Convert a single text into an embedding."""
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_documents(self, documents: list) -> list:
        """Convert multiple documents into embeddings."""
        embeddings = self.model.encode(documents)
        return embeddings.tolist() # tolist() converts numpy array to list for JSON serialization in Streamlit 