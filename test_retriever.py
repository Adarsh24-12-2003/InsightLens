
import chromadb

from src.retrieval.embeddings import EmbeddingService
from src.retrieval.retriever import Retriever


# 1. Create a temporary ChromaDB collection
client = chromadb.Client()

collection = client.create_collection(
    name="insightlens_test"
)

# 2. Create sample documents
documents = [
    "January revenue was 120 lakh.",
    "May revenue was 145 lakh.",
    "June revenue was 180 lakh."
]

# 3. Generate embeddings for sample documents
embedding_service = EmbeddingService()

embeddings = embedding_service.embed_documents(documents)

# 4. Store documents and embeddings in ChromaDB
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

# 5. Create the Retriever object
retriever = Retriever(collection, embedding_service)

# 6. Search for relevant documents
query = "Which month had the highest revenue?"

results = retriever.retrieve(query, top_k=3)

# 7. Display results
for result in results:
    print("Document:", result["text"])
    print("Distance:", result["distance"])
    print("Metadata:", result["metadata"])
    print("-" * 40)
