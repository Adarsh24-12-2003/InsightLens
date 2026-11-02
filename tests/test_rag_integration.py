import chromadb

from src.retrieval.rag_pipeline import RAGPipeline
from src.retrieval.retriever import Retriever


class SimpleEmbeddingService:
    def embed_text(self, text: str) -> list:
        terms = ("may", "june", "revenue")
        words = text.lower().split()
        return [float(term in words) for term in terms]


class SimpleLLMService:
    def generate_answer(self, query: str, context: list) -> str:
        return context[0]["text"]


def test_rag_pipeline_retrieves_context_for_non_numerical_question():
    client = chromadb.Client()
    collection = client.create_collection(name="rag_integration")
    embedding_service = SimpleEmbeddingService()
    documents = [
        "May revenue was 145 lakh.",
        "June revenue was 180 lakh.",
    ]
    collection.add(
        ids=["may", "june"],
        documents=documents,
        embeddings=[embedding_service.embed_text(document) for document in documents],
        metadatas=[{"month": "May"}, {"month": "June"}],
    )
    pipeline = RAGPipeline(
        Retriever(collection, embedding_service),
        SimpleLLMService(),
    )

    result = pipeline.ask("Tell me about June in this report.", top_k=1)

    assert result == {
        "answer": "June revenue was 180 lakh.",
        "sources": [{"month": "June"}],
    }
