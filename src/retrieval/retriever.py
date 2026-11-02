
class Retriever:  # Provides document retrieval from a ChromaDB collection.
    """Retrieve relevant documents from a ChromaDB collection."""

    def __init__(self, collection, embedding_service):  # Save the retrieval dependencies.
        self.collection = collection  # Keep the ChromaDB collection to search.
        self.embedding_service = embedding_service  # Keep the service that converts text to vectors.

    def retrieve(self, query: str, top_k: int = 5) -> list:  # Return the top matching documents.
        """Find the most relevant documents for a query."""

        query_embedding = self.embedding_service.embed_text(query)  # Embed the query for vector search.

        results = self.collection.query(  # Search the collection using the query vector.
            query_embeddings=[query_embedding],  # Pass the embedding in ChromaDB's expected list format.
            n_results=top_k,  # Limit the result count to the requested number.
            include=["documents", "metadatas", "distances"]  # Request text, metadata, and similarity distances.
        )

        retrieved_documents = []  # Accumulate results in the method's return format.

        for i, document in enumerate(results["documents"][0]):  # Pair each returned document with its result data.
            retrieved_documents.append({  # Convert this result into a single document record.
                "text": document,  # Store the matched document text.
                "metadata": results["metadatas"][0][i],  # Store metadata at the same result index.
                "distance": results["distances"][0][i]  # Store the distance at the same result index.
            })

        return retrieved_documents  # Return all matches in query order.
