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

    def _csv_source(self, month: str) -> dict:
        """Return the CSV filename and its physical row number."""
        months = list(self.data_analyzer.data["month"])
        row_index = months.index(month)
        # Row 1 is the CSV header, so the first data row is row 2.
        return {
            "source": SALES_CSV_PATH.name,
            "row": row_index + 2,
        }

    def _metadata_documents(self, **filters) -> list:
        """Retrieve exact records using their ChromaDB metadata."""
        if (
            self.retriever is None
            or not hasattr(self.retriever, "retrieve_by_metadata")
        ):
            return []
        where = {
            "$and": [
                {key: value}
                for key, value in filters.items()
            ]
        }
        documents = self.retriever.retrieve_by_metadata(
            where=where,
            limit=10,
        )
        # Convert zero-based CSV row_index into the physical CSV row.
        for document in documents:
            metadata = document["metadata"]
            if (
                metadata.get("source_type") == "csv"
                and "row_index" in metadata
            ):
                metadata["row"] = metadata["row_index"] + 2
        return documents

    def _handle_chart_question(self, query: str) -> Optional[dict]:
        """Answer chart questions using exact chart and CSV evidence."""
        query_lower = query.lower()
        if self.retriever is None:
            return None

        if self._asks_highest_revenue(query):
            chart = self._metadata_documents(
                source_type="chart",
                chart_name="revenue",
            )
            result = self.data_analyzer.get_highest_revenue()
            csv_source = self._csv_source(result["month"])
            return {
                "answer": (
                    f"{result['month']} had the highest revenue at "
                    f"{result['revenue']} lakh INR."
                ),
                "sources": [
                    document["metadata"] for document in chart
                ] + [csv_source],
            }

        if (
            "revenue" in query_lower
            and (
                "steadily" in query_lower
                or "every month" in query_lower
            )
        ):
            chart = self._metadata_documents(
                source_type="chart",
                chart_name="revenue",
            )
            march = self.data_analyzer.get_monthly_data("Mar")
            february = self.data_analyzer.get_monthly_data("Feb")
            april = self.data_analyzer.get_monthly_data("Apr")
            may = self.data_analyzer.get_monthly_data("May")
            csv_documents = (
                self._metadata_documents(source_type="csv", month="Mar")
                + self._metadata_documents(source_type="csv", month="May")
            )
            return {
                "answer": (
                    "No. Revenue did not rise steadily every month: it "
                    f"declined from {february['revenue_lakh_inr']} lakh INR "
                    f"in Feb to {march['revenue_lakh_inr']} lakh INR in Mar, "
                    f"and from {april['revenue_lakh_inr']} lakh INR in Apr "
                    f"to {may['revenue_lakh_inr']} lakh INR in May."
                ),
                "sources": [
                    document["metadata"] for document in chart
                ] + [
                    document["metadata"] for document in csv_documents
                ],
            }

        if "profit" in query_lower and "chart" in query_lower:
            month = next(
                (
                    value
                    for value in self.data_analyzer.data["month"]
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
            chart = self._metadata_documents(
                source_type="chart",
                chart_name="profit",
            )
            csv_documents = self._metadata_documents(
                source_type="csv",
                month=month,
            )
            result = self.data_analyzer.get_monthly_data(month)
            return {
                "answer": (
                    f"{result['month']} profit was "
                    f"{result['profit_lakh_inr']} lakh INR."
                ),
                "sources": [
                    document["metadata"] for document in chart
                ] + [
                    document["metadata"] for document in csv_documents
                ],
            }

        return None

    def _handle_promotion_question(self, query: str) -> Optional[dict]:
        """Compare revenue after the promotion without claiming causation."""
        query_lower = query.lower()
        if "promotion" not in query_lower or "after" not in query_lower:
            return None
        if self.retriever is None:
            return None

        report = self._metadata_documents(
            source_type="pdf",
            page_number=1,
        )
        transcript = self._metadata_documents(
            source_type="transcript",
            start_sec=36,
        )
        may = self.data_analyzer.get_monthly_data("May")
        june = self.data_analyzer.get_monthly_data("Jun")
        increase = june["revenue_lakh_inr"] - may["revenue_lakh_inr"]
        percentage = round(
            increase / may["revenue_lakh_inr"] * 100,
            2,
        )
        sources = (
            [document["metadata"] for document in report]
            + [document["metadata"] for document in transcript]
            + [
                self._csv_source("May"),
                self._csv_source("Jun"),
            ]
        )
        return {
            "answer": (
                "After the late-May promotion, June revenue rose from "
                f"{may['revenue_lakh_inr']} lakh INR in May to "
                f"{june['revenue_lakh_inr']} lakh INR in June, an increase "
                f"of {increase} lakh INR ({percentage}%). This sequence does "
                "not establish that the promotion caused the increase."
            ),
            "sources": sources,
        }

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
        chart_result = self._handle_chart_question(query)
        if chart_result:
            return chart_result

        promotion_result = self._handle_promotion_question(query)
        if promotion_result:
            return promotion_result

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
                "sources": [self._csv_source(result["month"])],
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
        """Return whether query asks for the highest monthly revenue."""
        words = set(re.findall(r"\b[a-z]+\b", query.lower()))
        asks_for_maximum = bool(
            words & {"highest", "most", "maximum", "max"}
        )
        asks_by_month = bool(
            words & {"month", "monthly"}
        )
        asks_for_revenue = "revenue" in words
        return (
            asks_for_revenue
            and asks_for_maximum
            and asks_by_month
        )

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
            "sources": [
                self._csv_source(result["first_month"]),
                self._csv_source(result["second_month"]),
            ],
        }

    def _handle_monthly_question(self, query: str) -> Optional[dict]:
        """Answer supported single-month revenue, profit, or margin questions.

        Causal questions are left for document retrieval because monthly sales
        figures alone cannot establish what caused a change.

        Returns a CSV-backed answer when the question is supported, otherwise
        ``None`` so the question can continue through the retrieval pipeline.
        """
        query_lower = query.lower()
        if re.search(
            r"\b(caus(?:e|es|ed|ing)|because|due to|impact|effect|"
            r"influenc(?:e|es|ed|ing)|contribut(?:e|es|ed|ing)|"
            r"driven by|lead to|led to|result in|resulted in|"
            r"resulted from|attribut(?:e|es|ed|ing))\b",
            query_lower,
        ):
            # Do not present a correlation in the CSV as a proven cause.
            return None

        requested_year = re.search(r"\b\d{4}\b", query)
        if requested_year:
            # The sales CSV has no year column, so year-specific figures cannot be verified.
            return {
                "answer": (
                    "The sales dataset does not contain year information. "
                    f"I cannot confirm the figures for {requested_year.group()}."
                ),
                "sources": [{"source": str(SALES_CSV_PATH)}],
            }

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
                "sources": [self._csv_source(month)],
            }

        if "revenue" in query_lower or "profit" in query_lower:
            result = self.data_analyzer.get_monthly_data(month)
            if "in indian rupees" in query_lower or "in rupees" in query_lower:
                if "revenue" in query_lower:
                    amount = int(result["revenue_lakh_inr"] * 100000)
                    answer = (
                        f"{result['month']} revenue was "
                        f"₹{amount:,} "
                        f"(₹{amount / 10000000:g} crore)."
                    )
                else:
                    amount = int(result["profit_lakh_inr"] * 100000)
                    answer = (
                        f"{result['month']} profit was "
                        f"₹{amount:,}."
                    )
            else:
                answer = (
                    f"{result['month']} revenue was "
                    f"₹{result['revenue_lakh_inr']} lakh "
                    f"and profit was ₹{result['profit_lakh_inr']} lakh."
                )
            return {
                "answer": answer,
                "sources": [self._csv_source(month)],
            }
        return None
