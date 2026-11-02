
from src.retrieval.llm import LLMService

llm = LLMService()

context = [
    {
        "text": "June revenue was 180 lakh.",
        "metadata": {
            "source_type": "csv",
            "month": "June"
        }
    },
    {
        "text": "May revenue was 145 lakh.",
        "metadata": {
            "source_type": "csv",
            "month": "May"
        }
    }
]

question = "What was the revenue in June?"

answer = llm.generate_answer(question, context)

print("Question:", question)
print("Answer:", answer)
