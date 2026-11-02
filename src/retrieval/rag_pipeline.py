
import re  # Match words and month names in questions.
from pathlib import Path  # Build a path to the sales CSV.
from typing import Optional  # Mark results that may be absent.

from src.analysis.data_analyzer import DataAnalyzer  # Calculate trusted values from the CSV.
from src.retrieval.retriever import Retriever  # Import the document retrieval component.
from src.retrieval.llm import LLMService  # Import the answer-generation component.

SALES_CSV_PATH = Path(__file__).resolve().parents[2] / "data/raw/G3_sales_ground_truth.csv"  # Locate the source data.
MONTH_NAMES = {  # Map CSV month abbreviations to full names.
    "jan": "january",  # Expand January.
    "feb": "february",  # Expand February.
    "mar": "march",  # Expand March.
    "apr": "april",  # Expand April.
    "may": "may",  # Keep May unchanged.
    "jun": "june",  # Expand June.
    "jul": "july",  # Expand July.
    "aug": "august",  # Expand August.
    "sep": "september",  # Expand September.
    "oct": "october",  # Expand October.
    "nov": "november",  # Expand November.
    "dec": "december",  # Expand December.
}


class RAGPipeline:  # Coordinate retrieval and answer generation.
    """Connect retrieval and answer generation."""

    def __init__(  # Initialize the pipeline and its services.
        self,  # Refer to this pipeline instance.
        retriever: Optional[Retriever] = None,  # Allow numerical questions without retrieval.
        llm: Optional[LLMService] = None,  # Allow numerical questions without an LLM.
    ):  # Finish the constructor signature.
        self.retriever = retriever  # Save the document retriever.
        self.llm = llm  # Save the language model service.
        self.data_analyzer = DataAnalyzer(str(SALES_CSV_PATH))  # Load trusted numerical data.

    def ask(self, query: str, top_k: int = 5) -> dict:  # Answer a question using retrieved documents.
        """Retrieve relevant context and generate an answer."""

        if self._asks_highest_revenue(query):  # Handle highest-revenue questions with exact CSV data.
            result = self.data_analyzer.get_highest_revenue()  # Find the maximum directly from the CSV.
            return {  # Return the calculated answer and its source.
                "answer": (  # Format the highest-revenue result.
                    f"{result['month']} had the highest revenue at "  # State which month was highest.
                    f"{result['revenue']} lakh INR."  # Include its revenue amount.
                ),  # Finish formatting the answer.
                "sources": [{"source": SALES_CSV_PATH.name}],  # Cite the CSV file.
            }  # Finish the result.

        monthly_result = self._handle_monthly_question(query)  # Check for a month-specific calculation.
        if monthly_result:  # Use the result when the question was handled.
            return monthly_result  # Return the CSV-backed answer.

        if self.retriever is None or self.llm is None:  # Ensure services exist for other questions.
            raise ValueError(  # Report missing dependencies clearly.
                "Retriever and LLM services are required for non-numerical questions."  # Explain what is required.
            )  # Finish raising the error.

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

    @staticmethod  # This check does not need pipeline state.
    def _asks_highest_revenue(query: str) -> bool:  # Identify questions asking for maximum revenue.
        words = set(re.findall(r"\b[a-z]+\b", query.lower()))  # Extract lowercase words from the query.
        asks_for_maximum = bool(words & {"highest", "most", "maximum", "max"})  # Check for maximum terms.
        return "revenue" in words and asks_for_maximum  # Require both revenue and a maximum term.

    def _handle_monthly_question(self, query: str) -> Optional[dict]:  # Handle supported monthly questions.
        """Handle monthly revenue, profit, and margin questions."""
        query_lower = query.lower()  # Normalize text for matching.
        month = next(  # Find the first CSV month mentioned in the query.
            (
                value for value in self.data_analyzer.data["month"]  # Check each month in the CSV.
                if re.search(rf"\b{re.escape(value.lower())}\b", query_lower)  # Match its exact abbreviation.
                or re.search(  # Also check the full month name.
                    rf"\b{re.escape(MONTH_NAMES.get(value.lower(), value.lower()))}\b",  # Convert abbreviation when known.
                    query_lower,  # Search the normalized query.
                )  # Finish full-name matching.
            ),  # Finish selecting a matching month.
            None,  # Return no month when none is mentioned.
        )  # Store the matching month, if any.

        if month is None:  # Check whether a month was found.
            return None  # Let the regular RAG flow handle the question.

        if "margin" in query_lower:  # Handle questions about profit margin.
            result = self.data_analyzer.calculate_profit_margin(month)  # Calculate the margin from CSV values.
            return {  # Return the margin and its source.
                "answer": (  # Format the margin answer.
                    f"{result['month']} profit margin was "  # State the month.
                    f"{result['profit_margin']}%."  # Include the percentage.
                ),  # Finish formatting the answer.
                "sources": [{"source": SALES_CSV_PATH.name}],  # Cite the CSV file.
            }  # Finish the result.

        if "revenue" in query_lower or "profit" in query_lower:  # Handle monthly revenue or profit questions.
            result = self.data_analyzer.get_monthly_data(month)  # Get that month's CSV values.
            return {  # Return the values and their source.
                "answer": (  # Format the monthly answer.
                    f"{result['month']} revenue was "  # State the month and revenue.
                    f"₹{result['revenue_lakh_inr']} lakh "  # Include revenue in lakh rupees.
                    f"and profit was ₹{result['profit_lakh_inr']} lakh."  # Include profit in lakh rupees.
                ),  # Finish formatting the answer.
                "sources": [{"source": SALES_CSV_PATH.name}],  # Cite the CSV file.
            }  # Finish the result.

        return None  # Leave unrelated monthly questions to the regular RAG flow.
