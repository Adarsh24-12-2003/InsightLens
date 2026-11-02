from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "Which month had the highest revenue?",
    "When did sales reach their maximum?",
    "What is the weather today?"
]

embeddings = model.encode(sentences)

similarity = cosine_similarity(embeddings)

print(similarity)
