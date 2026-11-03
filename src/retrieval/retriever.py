
"""Find documents whose embeddings are similar to a user's query."""


class Retriever:
    """Search a ChromaDB collection and return its closest matching documents."""

    def __init__(self, collection, embedding_service):
        """Store the collection and service used to encode search queries."""
        self.collection = collection
        self.embedding_service = embedding_service

    def retrieve(self, query: str, top_k: int = 5) -> list:
        """Return up to ``top_k`` matches with their text, metadata, and distance.

        The query is embedded with the same service used for stored documents,
        allowing ChromaDB to compare vectors rather than exact words.

        Args:
            query: Text to search for.
            top_k: Maximum number of matches to return.

        Returns:
            A list of matching document records.
        """
        query_embedding = self.embedding_service.embed_text(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        retrieved_documents = []
        for i, document in enumerate(results["documents"][0]):
            retrieved_documents.append({
                "text": document,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })

        return retrieved_documents
