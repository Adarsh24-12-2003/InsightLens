
"""Build grounded prompts and generate answers with Google's Gemini model."""

import os

from dotenv import load_dotenv
from google import genai


class LLMService:
    """Generate answers using retrieved context and Gemini."""

    def __init__(self):
        """Load credentials and create the Gemini client."""
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")

        self.client = genai.Client(api_key=api_key)

        self.model = "gemini-2.5-flash"

    def generate_answer(self, query: str, context: list) -> str:
        """Send a grounded prompt to Gemini and return its generated answer.

        Each document's metadata is included with its text so the model can
        identify the source while answering from the supplied context.

        Args:
            query: The user's question.
            context: Retrieved document records containing text and metadata.

        Returns:
            The answer text returned by Gemini.
        """
        context_text = "\n\n".join(
            [
                f"Source: {item['metadata']}\n"
                f"Content: {item['text']}"
                for item in context
            ]
        )

        prompt = f"""
        You are an assistant answering questions about business data.

        Answer the user's question using ONLY the provided context.

        Rules:
        1. Do not invent information.
        2. If the context does not contain the answer, say that
           sufficient information is not available.
        3. Keep the answer clear and concise.
        4. Mention the available sources.

        Retrieved Context:
        {context_text}

        User Question:
        {query}

        Answer:
        """

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text
