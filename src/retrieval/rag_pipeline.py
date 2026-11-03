"""Route questions to trusted calculations or retrieval-based answers."""

import re
from pathlib import Path
from typing import Optional

from src.analysis.data_analyzer import DataAnalyzer
from src.retrieval.llm import LLMService
from src.retrieval.retriever import Retriever

SALES_CSV_PATH = (
    Path(__file__).resolve().parents[2]
    / "data/raw/G3_sales_ground_truth.csv"
)
MONTH_NAMES = {
    "jan": "january",
    "feb": "february",
    "mar": "march",
    "apr": "april",
    "may": "may",
    "jun": "june",
    "jul": "july",
    "aug": "august",
    "sep": "september",
    "oct": "october",
    "nov": "november",
    "dec": "december",
}


class RAGPipeline:
    """Answer business questions with CSV calculations or retrieved documents.

    Questions supported by the sales data are calculated directly. Other
    questions use retrieval-augmented generation (RAG): find relevant text,
    then provide that text to a language model as answer context.
    """

    def __init__(
        self,
        retriever: Optional[Retriever] = None,
        llm: Optional[LLMService] = None,
    ):
        """Set up optional retrieval services and load the trusted sales data."""
        self.retriever = retriever
        self.llm = llm
        self.data_analyzer = DataAnalyzer(str(SALES_CSV_PATH))

    def ask(self, query: str, top_k: int = 5) -> dict:
        """Answer ``query`` and include the sources used.

        Supported numerical questions are answered from the CSV. Other
        questions are answered from retrieved context and require both a
        retriever and a language-model service.

        Args:
            query: The user's question.
            top_k: Maximum number of documents to retrieve for RAG answers.

        Returns:
            A dictionary containing the answer and its sources.

        Raises:
            ValueError: If a non-numerical question needs services that are
                not configured.
        """
        comparison_result = self._handle_margin_comparison(query)
        if comparison_result:
            return comparison_result

        if self._asks_highest_revenue(query):
            result = self.data_analyzer.get_highest_revenue()
            return {
                "answer": (
                    f"{result['month']} had the highest revenue at "
                    f"{result['revenue']} lakh INR."
                ),
                "sources": [{"source": SALES_CSV_PATH.name}],
            }

        monthly_result = self._handle_monthly_question(query)
        if monthly_result:
            return monthly_result

        if self.retriever is None or self.llm is None:
            raise ValueError(
                "Retriever and LLM services are required for "
                "non-numerical questions."
            )

        retrieved_documents = self.retriever.retrieve(
            query=query,
            top_k=top_k
        )

        if not retrieved_documents:
            return {
                "answer": (
                    "I could not find relevant information to "
                    "answer this question."
                ),
                "sources": []
            }

        answer = self.llm.generate_answer(
            query=query,
            context=retrieved_documents
        )

        sources = [
            document["metadata"]
            for document in retrieved_documents
        ]

        return {
            "answer": answer,
            "sources": sources
        }

    @staticmethod
    def _asks_highest_revenue(query: str) -> bool:
        """Return whether ``query`` asks for a revenue maximum."""
        words = set(re.findall(r"\b[a-z]+\b", query.lower()))
        asks_for_maximum = bool(words & {"highest", "most", "maximum", "max"})
        return "revenue" in words and asks_for_maximum

    def _handle_margin_comparison(self, query: str) -> Optional[dict]:
        """Answer a comparison question using the order in which months appear.

        Month names may use either the CSV abbreviation or the full name.
        Keeping their positions in the question preserves which month is being
        evaluated against the comparison month.

        Returns:
            A CSV-backed answer, or ``None`` if the question does not mention
            two months and a profit margin.
        """
        query_lower = query.lower()
        if "margin" not in query_lower:
            return None

        months = {
            month.lower(): month
            for month in self.data_analyzer.data["month"]
        }
        month_matches = []
        for normalized_month, month in months.items():
            full_month = MONTH_NAMES.get(
                normalized_month,
                normalized_month
            )
            abbreviation_match = re.search(
                rf"\b{re.escape(normalized_month)}\b",
                query_lower
            )
            full_name_match = re.search(
                rf"\b{re.escape(full_month)}\b",
                query_lower
            )
            matches = [
                match for match in (
                    abbreviation_match,
                    full_name_match
                )
                if match
            ]
            if matches:
                # Sorting by text position preserves the user's comparison order.
                month_matches.append(
                    (min(match.start() for match in matches), month)
                )
        month_matches.sort(key=lambda item: item[0])
        if len(month_matches) < 2:
            return None
        first_month = month_matches[0][1]
        second_month = month_matches[1][1]

        result = self.data_analyzer.compare_profit_margins(
            first_month,
            second_month,
        )
        if "error" in result:
            return {
                "answer": result["error"],
                "sources": [{"source": SALES_CSV_PATH.name}],
            }

        difference = round(
            result["first_margin"] - result["second_margin"],
            2
        )
        if difference > 0:
            answer = (
                f"Yes, profit margin improved from {result['second_margin']}% in "
                f"{result['second_month']} to {result['first_margin']}% in "
                f"{result['first_month']}, an increase of {difference} percentage points."
            )
        elif difference == 0:
            answer = (
                f"No, profit margin remained at {result['first_margin']}% in "
                f"{result['first_month']} and {result['second_month']}."
            )
        else:
            answer = (
                f"No, profit margin declined from {result['second_margin']}% in "
                f"{result['second_month']} to {result['first_margin']}% in "
                f"{result['first_month']}, a decrease of "
                f"{abs(difference)} percentage points."
            )

        return {
            "answer": answer,
            "sources": [{"source": SALES_CSV_PATH.name}],
        }

    def _handle_monthly_question(self, query: str) -> Optional[dict]:
        """Answer supported single-month revenue, profit, or margin questions.

        Returns a CSV-backed answer when the question is supported, otherwise
        ``None`` so the question can continue through the retrieval pipeline.
        """
        query_lower = query.lower()
        month = next(
            (
                value for value in self.data_analyzer.data["month"]
                if re.search(rf"\b{re.escape(value.lower())}\b", query_lower)
                or re.search(
                    rf"\b{re.escape(MONTH_NAMES.get(value.lower(), value.lower()))}\b",
                    query_lower,
                )
            ),
            None,
        )

        if month is None:
            return None

        if "margin" in query_lower:
            result = self.data_analyzer.calculate_profit_margin(month)
            return {
                "answer": (
                    f"{result['month']} profit margin was "
                    f"{result['profit_margin']}%."
                ),
                "sources": [{"source": SALES_CSV_PATH.name}],
            }

        if "revenue" in query_lower or "profit" in query_lower:
            result = self.data_analyzer.get_monthly_data(month)
            return {
                "answer": (
                    f"{result['month']} revenue was "
                    f"₹{result['revenue_lakh_inr']} lakh "
                    f"and profit was ₹{result['profit_lakh_inr']} lakh."
                ),
                "sources": [{"source": SALES_CSV_PATH.name}],
            }

        return None
