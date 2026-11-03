"""Create vector representations of text for semantic search."""

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Turn text into numeric vectors with a Sentence Transformers model."""

    def __init__(self):
        """Load the model used to encode queries and documents."""
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_text(self, text: str) -> list:
        """Return a list of numbers representing one text."""
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_documents(self, documents: list) -> list:
        """Return one vector for each document, in input order."""
        embeddings = self.model.encode(documents)
        return embeddings.tolist()