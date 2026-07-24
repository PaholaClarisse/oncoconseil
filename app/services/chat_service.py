from app.services.document_processor import generate_embedding
from app.vector_db import collection

def search_relevant_chunks(question: str, n_results: int = 3):
    question_embedding = generate_embedding(question)

    results = collection.query(query_embeddings=[question_embedding],n_results=n_results)

    return results