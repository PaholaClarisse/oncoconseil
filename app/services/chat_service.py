from app.services.document_processor import generate_embedding
from app.vector_db import collection

def search_relevant_chunks(question: str, n_results: int = 3):
    question_embedding = generate_embedding(question)

    results = collection.query(query_embeddings=[question_embedding],n_results=n_results)

    return results

SIMILARITY_THRESHOLD = 0.5

def is_within_scope(distances: list) -> bool:
    meilleure_distance = distances[0][0]
    return meilleure_distance < SIMILARITY_THRESHOLD

def check_scope(question: str):
    results = search_relevant_chunks(question)
    if not is_within_scope(results["distances"]):
        return None  # hors périmètre
    return results  # dans le périmètre, chunks utilisables