
"""Build grounded prompts and generate answers with Google's Gemini model."""

import json
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
                f"Source metadata: {json.dumps(item['metadata'], ensure_ascii=False)}\n"
                f"Content: {item['text']}"
                for item in context
            ]
        )

        prompt = f"""
        You are InsightLens, a multimodal business data assistant.
        Answer the user's question using ONLY the retrieved context.
        Rules:
        1. Never invent facts, numbers, sources, or timestamps.
        2. If the evidence is insufficient, clearly say so.
        3. Use exact figures and details from the context.
        4. Cite the sources that support your answer.
        5. Include PDF page numbers when available.
        6. Include transcript timestamps when available.
        7. Identify chart sources when available.
        8. Do not create page numbers or timestamps if they are missing.
        9. If sources disagree, explain the disagreement.
        10. Keep the answer clear and concise.

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

        return response.text or "I could not generate an answer based on the provided context."
