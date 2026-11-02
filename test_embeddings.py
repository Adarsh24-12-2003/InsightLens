from src.retrieval.embeddings import EmbeddingService


service = EmbeddingService()

# Test one sentence
text = "June revenue was 180 lakh"

vector = service.embed_text(text)

print("Single embedding dimension:", len(vector))


# Test multiple sentences
documents = [
    "June revenue was 180 lakh",
    "May revenue was 145 lakh",
    "January revenue was 120 lakh"
]

vectors = service.embed_documents(documents)

print("Number of embeddings:", len(vectors))
print("Dimension:", len(vectors[0]))

print("Embedding test successful!")
