"""Test numerical routing and retrieval fallbacks in the RAG pipeline."""

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
        "sources": [{"source": "G3_sales_ground_truth.csv", "row": 7}],
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
    retriever.retrieve_by_metadata.return_value = [
        {"metadata": {"source_name": "G3_revenue_chart.png"}}
    ]
    llm = Mock()
    pipeline = RAGPipeline(retriever, llm)

    result = pipeline.ask("Which month had the highest revenue?")

    assert result == {
        "answer": "Jun had the highest revenue at 180 lakh INR.",
        "sources": [
            {"source_name": "G3_revenue_chart.png"},
            {"source": "G3_sales_ground_truth.csv", "row": 7},
        ],
    }
    retriever.retrieve.assert_not_called()
    llm.generate_answer.assert_not_called()


def test_ask_uses_csv_for_maximum_monthly_revenue_without_retrieval_services():
    pipeline = RAGPipeline()

    result = pipeline.ask("What was the maximum monthly revenue?")

    assert result == {
        "answer": "Jun had the highest revenue at 180 lakh INR.",
        "sources": [{"source": "G3_sales_ground_truth.csv", "row": 7}],
    }


def test_highest_revenue_detection_requires_monthly_scope():
    assert not RAGPipeline._asks_highest_revenue("What was the maximum revenue?")


def test_chart_trend_answer_cites_chart_and_csv_rows():
    retriever = Mock()
    retriever.retrieve_by_metadata.side_effect = [
        [{"metadata": {"source_name": "G3_revenue_chart.png"}}],
        [{
            "metadata": {
                "source_type": "csv",
                "source": "G3_sales_ground_truth.csv",
                "row_index": 2,
            }
        }],
        [{
            "metadata": {
                "source_type": "csv",
                "source": "G3_sales_ground_truth.csv",
                "row_index": 4,
            }
        }],
    ]
    pipeline = RAGPipeline(retriever, Mock())

    result = pipeline.ask("Did the revenue chart rise steadily every month?")

    assert "did not rise steadily" in result["answer"]
    assert "declined from 130 lakh INR in Feb to 125 lakh INR in Mar" in result["answer"]
    assert [source.get("row") for source in result["sources"][1:]] == [4, 6]


def test_promotion_answer_cites_report_transcript_and_csv_rows():
    retriever = Mock()
    retriever.retrieve_by_metadata.side_effect = [
        [{"metadata": {"source_name": "G3_business_report.pdf", "page_number": 1}}],
        [{
            "metadata": {
                "source_name": "G3_video_transcript.json",
                "start_sec": 36,
            }
        }],
    ]
    pipeline = RAGPipeline(retriever, Mock())

    result = pipeline.ask("What happened after the late-May promotion?")

    assert "145 lakh INR in May to 180 lakh INR in June" in result["answer"]
    assert "35 lakh INR (24.14%)" in result["answer"]
    assert "does not establish" in result["answer"]
    assert [source.get("row") for source in result["sources"][-2:]] == [6, 7]


def test_ask_uses_csv_for_monthly_revenue_and_profit():
    pipeline = RAGPipeline()

    result = pipeline.ask("What were the revenue and profit in May?")

    assert result == {
        "answer": "May revenue was ₹145 lakh and profit was ₹20 lakh.",
        "sources": [{"source": "G3_sales_ground_truth.csv", "row": 6}],
    }


def test_ask_converts_revenue_to_rupees_and_crore():
    pipeline = RAGPipeline()

    result = pipeline.ask("What was the revenue in June in Indian rupees?")

    assert result["answer"] == "Jun revenue was ₹18,000,000 (₹1.8 crore)."


def test_ask_converts_profit_to_rupees():
    pipeline = RAGPipeline()

    result = pipeline.ask("What was the profit in June in rupees?")

    assert result["answer"] == "Jun profit was ₹2,900,000."


def test_ask_matches_full_month_name_to_csv_abbreviation():
    pipeline = RAGPipeline()

    result = pipeline.ask("What was the revenue in June?")

    assert result["answer"] == "Jun revenue was ₹180 lakh and profit was ₹29 lakh."


def test_ask_uses_csv_for_monthly_profit_margin():
    pipeline = RAGPipeline()

    result = pipeline.ask("What was the profit margin in May?")

    assert result == {
        "answer": "May profit margin was 13.79%.",
        "sources": [{"source": "G3_sales_ground_truth.csv", "row": 6}],
    }


def test_ask_uses_csv_to_compare_profit_margins():
    pipeline = RAGPipeline()

    result = pipeline.ask(
        "Did profit margin definitely improve in June compared with May?"
    )

    assert result == {
        "answer": (
            "Yes, profit margin improved from 13.79% in May to 16.11% in "
            "Jun, an increase of 2.32 percentage points."
        ),
        "sources": [
            {"source": "G3_sales_ground_truth.csv", "row": 7},
            {"source": "G3_sales_ground_truth.csv", "row": 6},
        ],
    }


def test_ask_compares_margin_in_first_mentioned_month_to_second():
    pipeline = RAGPipeline()

    result = pipeline.ask(
        "Did profit margin improve in May compared with June?"
    )

    assert result == {
        "answer": (
            "No, profit margin declined from 16.11% in Jun to 13.79% in "
            "May, a decrease of 2.32 percentage points."
        ),
        "sources": [
            {"source": "G3_sales_ground_truth.csv", "row": 6},
            {"source": "G3_sales_ground_truth.csv", "row": 7},
        ],
    }


def test_non_numerical_question_requires_retrieval_services():
    pipeline = RAGPipeline()

    with pytest.raises(
        ValueError,
        match=(
            "Retriever and LLM services are required for "
            "non-numerical questions."
        ),
    ):
        pipeline.ask("What does the report say?")
