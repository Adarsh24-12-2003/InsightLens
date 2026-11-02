from unittest.mock import Mock

import pytest

from src.retrieval.rag_pipeline import RAGPipeline


def test_ask_uses_csv_for_monthly_revenue():
    retriever = Mock()
    llm = Mock()
    pipeline = RAGPipeline(retriever, llm)

    result = pipeline.ask("What was June revenue?", top_k=2)

    assert result == {
        "answer": "Jun revenue was ₹180 lakh and profit was ₹29 lakh.",
        "sources": [{"source": "G3_sales_ground_truth.csv"}],
    }
    retriever.retrieve.assert_not_called()
    llm.generate_answer.assert_not_called()


def test_ask_returns_fallback_when_no_documents_are_found():
    retriever = Mock()
    retriever.retrieve.return_value = []
    llm = Mock()
    pipeline = RAGPipeline(retriever, llm)

    result = pipeline.ask("What does the report say?")

    assert result == {
        "answer": "I could not find relevant information to answer this question.",
        "sources": [],
    }
    llm.generate_answer.assert_not_called()


def test_ask_uses_csv_for_highest_revenue_question():
    retriever = Mock()
    llm = Mock()
    pipeline = RAGPipeline(retriever, llm)

    result = pipeline.ask("Which month had the highest revenue?")

    assert result == {
        "answer": "Jun had the highest revenue at 180 lakh INR.",
        "sources": [{"source": "G3_sales_ground_truth.csv"}],
    }
    retriever.retrieve.assert_not_called()
    llm.generate_answer.assert_not_called()


def test_ask_uses_csv_for_maximum_revenue_without_retrieval_services():
    pipeline = RAGPipeline()

    result = pipeline.ask("What was the maximum revenue?")

    assert result == {
        "answer": "Jun had the highest revenue at 180 lakh INR.",
        "sources": [{"source": "G3_sales_ground_truth.csv"}],
    }


def test_ask_uses_csv_for_monthly_revenue_and_profit():
    pipeline = RAGPipeline()

    result = pipeline.ask("What were the revenue and profit in May?")

    assert result == {
        "answer": "May revenue was ₹145 lakh and profit was ₹20 lakh.",
        "sources": [{"source": "G3_sales_ground_truth.csv"}],
    }


def test_ask_matches_full_month_name_to_csv_abbreviation():
    pipeline = RAGPipeline()

    result = pipeline.ask("What was the revenue in June?")

    assert result["answer"] == "Jun revenue was ₹180 lakh and profit was ₹29 lakh."


def test_ask_uses_csv_for_monthly_profit_margin():
    pipeline = RAGPipeline()

    result = pipeline.ask("What was the profit margin in May?")

    assert result == {
        "answer": "May profit margin was 13.79%.",
        "sources": [{"source": "G3_sales_ground_truth.csv"}],
    }


def test_non_numerical_question_requires_retrieval_services():
    pipeline = RAGPipeline()

    with pytest.raises(
        ValueError,
        match="Retriever and LLM services are required for non-numerical questions.",
    ):
        pipeline.ask("What does the report say?")
