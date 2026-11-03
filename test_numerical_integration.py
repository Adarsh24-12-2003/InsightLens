
"""Run example business questions through the CSV-backed numerical pipeline."""

from src.retrieval.rag_pipeline import RAGPipeline


pipeline = RAGPipeline(
    retriever=None,
    llm=None
)

questions = [
    "Which month had the highest revenue?",
    "What was the revenue in June?",
    "What was the profit margin in May?",
    "Did profit margin improve in June compared with May?",
    "Did profit margin improve in May compared with June?"
]

for question in questions:
    result = pipeline.ask(question)

    print("\nQuestion:", question)
    print("Answer:", result["answer"])
    print("Sources:", result["sources"])
