from unittest.mock import Mock

from src.retrieval.rag_pipeline import RAGPipeline


def test_ask_returns_answer_and_sources():
    documents = [
        {"text": "June revenue was 180 lakh.", "metadata": {"month": "June"}},
        {"text": "May revenue was 145 lakh.", "metadata": {"month": "May"}},
    ]
    retriever = Mock()
    retriever.retrieve.return_value = documents
    llm = Mock()
    llm.generate_answer.return_value = "June revenue was 180 lakh."
    pipeline = RAGPipeline(retriever, llm)

    result = pipeline.ask("What was June revenue?", top_k=2)

    assert result == {
        "answer": "June revenue was 180 lakh.",
        "sources": [{"month": "June"}, {"month": "May"}],
    }
    retriever.retrieve.assert_called_once_with(query="What was June revenue?", top_k=2)
    llm.generate_answer.assert_called_once_with(
        query="What was June revenue?",
        context=documents,
    )


def test_ask_returns_fallback_when_no_documents_are_found():
    retriever = Mock()
    retriever.retrieve.return_value = []
    llm = Mock()
    pipeline = RAGPipeline(retriever, llm)

    result = pipeline.ask("What was June revenue?")

    assert result == {
        "answer": "I could not find relevant information to answer this question.",
        "sources": [],
    }
    llm.generate_answer.assert_not_called()
