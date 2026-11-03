
"""Smoke-test embedding-based document search with a temporary collection."""

import chromadb

from src.retrieval.embeddings import EmbeddingService
from src.retrieval.retriever import Retriever


client = chromadb.Client()
collection = client.create_collection(
    name="insightlens_test"
)

documents = [
    "January revenue was 120 lakh.",
    "May revenue was 145 lakh.",
    "June revenue was 180 lakh."
]

embedding_service = EmbeddingService()
embeddings = embedding_service.embed_documents(documents)

collection.add(
    ids=["doc1", "doc2", "doc3"],
    documents=documents,
    embeddings=embeddings,
    metadatas=[
        {"source_type": "csv", "month": "January"},
        {"source_type": "csv", "month": "May"},
        {"source_type": "csv", "month": "June"}
    ]
)

retriever = Retriever(collection, embedding_service)
query = "Which month had the highest revenue?"
results = retriever.retrieve(query, top_k=3)

for result in results:
    print("Document:", result["text"])
    print("Distance:", result["distance"])
    print("Metadata:", result["metadata"])
    print("-" * 40)
