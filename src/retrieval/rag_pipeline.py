
from src.retrieval.retriever import Retriever  # Import the document retrieval component.
from src.retrieval.llm import LLMService  # Import the answer-generation component.


class RAGPipeline:  # Coordinate retrieval and answer generation.
    """Connect retrieval and answer generation."""

    def __init__(self, retriever: Retriever, llm: LLMService):  # Receive the pipeline components.
        self.retriever = retriever  # Save the document retriever.
        self.llm = llm  # Save the language model service.

    def ask(self, query: str, top_k: int = 5) -> dict:  # Answer a question using retrieved documents.
        """Retrieve relevant context and generate an answer."""

        # 1. Retrieve relevant documents.
        retrieved_documents = self.retriever.retrieve(  # Search for documents matching the question.
            query=query,  # Pass the user's question.
            top_k=top_k  # Limit the number of retrieved documents.
        )  # Store the matching documents.

        # 2. Check whether any documents were retrieved.
        if not retrieved_documents:  # Handle an empty retrieval result.
            return {  # Return a clear answer and no sources.
                "answer": "I could not find relevant information to answer this question.",  # Explain that no context was found.
                "sources": []  # Provide an empty source list.
            }  # Stop without calling the language model.

        # 3. Generate an answer using retrieved context.
        answer = self.llm.generate_answer(  # Ask the language model to respond.
            query=query,  # Pass along the original question.
            context=retrieved_documents  # Ground the response in retrieved documents.
        )  # Store the generated answer.

        # 4. Collect source metadata.
        sources = [  # Build a list of the documents' source metadata.
            document["metadata"]  # Select metadata from each document.
            for document in retrieved_documents  # Visit every retrieved document.
        ]  # Store the collected source metadata.

        # 5. Return answer and sources.
        return {  # Package the answer and source list together.
            "answer": answer,  # Include the generated response.
            "sources": sources  # Include metadata for its supporting documents.
        }  # Return the pipeline result.
