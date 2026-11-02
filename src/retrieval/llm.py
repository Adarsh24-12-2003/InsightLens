
import os  # Read the API key from the environment.

from dotenv import load_dotenv  # Load variables from a local .env file.
from google import genai  # Use Google's Gemini client.


class LLMService:  # Encapsulate Gemini-based answer generation.
    """Generate answers using retrieved context and Gemini."""

    def __init__(self):  # Initialize the Gemini client and model.
        load_dotenv()  # Make .env variables available through os.environ.

        api_key = os.getenv("GEMINI_API_KEY")  # Read the Gemini API credential.

        if not api_key:  # Ensure the client can be authenticated.
            raise ValueError("GEMINI_API_KEY not found in .env file")  # Report the missing required setting.

        self.client = genai.Client(api_key=api_key)  # Create an authenticated Gemini client.

        self.model = "gemini-2.5-flash"  # Select the model used for answer generation.

    def generate_answer(self, query: str, context: list) -> str:  # Generate an answer grounded in retrieved context.
        """Generate an answer using the retrieved documents."""

        context_text = "\n\n".join(  # Separate each source and its content with a blank line.
            [
                f"Source: {item['metadata']}\n"  # Include the document's metadata as its source.
                f"Content: {item['text']}"  # Include the retrieved document text.
                for item in context  # Format every retrieved document.
            ]  # Finish collecting the formatted document strings.
        )  # Join the formatted documents into one context block.

        # Build instructions and provide the retrieved context and user question.
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
        """  # Finish the prompt without changing its text.

        response = self.client.models.generate_content(  # Request an answer from the configured Gemini model.
            model=self.model,  # Specify which model should generate the answer.
            contents=prompt  # Send the complete prompt as model input.
        )  # Finish the Gemini content-generation request.

        return response.text  # Return the generated answer text.
