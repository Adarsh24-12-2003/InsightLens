
"""Find documents using semantic similarity or metadata filters."""


class Retriever:
    """Search a ChromaDB collection for relevant documents."""

    def __init__(self, collection, embedding_service):
        """Store the collection and query embedding service."""
        self.collection = collection
        self.embedding_service = embedding_service

    def retrieve(self, query: str, top_k: int = 5) -> list:
        """Return documents closest to the user's semantic query."""
        query_embedding = self.embedding_service.embed_text(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        retrieved_documents = []

        for i, document in enumerate(results["documents"][0]):
            retrieved_documents.append({
                "text": document,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })

        return retrieved_documents

    def retrieve_by_metadata(
        self,
        where: dict,
        limit: int = 10,
    ) -> list:
        """Return documents matching exact ChromaDB metadata filters."""
        results = self.collection.get(
            where=where,
            limit=limit,
            include=["documents", "metadatas"],
        )

        retrieved_documents = []

        for i, document in enumerate(results["documents"]):
            retrieved_documents.append({
                "text": document,
                "metadata": results["metadatas"][i],
                "distance": None,
            })

        return retrieved_documents
