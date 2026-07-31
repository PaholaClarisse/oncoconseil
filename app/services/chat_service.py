from app.services.document_processor import generate_embedding
from app.vector_db import collection
import google.generativeai as genai
from app.config import settings
genai.configure(api_key=settings.LLM_API_KEY)

# fonction pour rechercher les chunks pertinents à partir d'une question
def search_relevant_chunks(question: str, n_results: int = 3):
    question_embedding = generate_embedding(question)
    results = collection.query(query_embeddings=[question_embedding],n_results=n_results)
    return results # retourne les chunks pertinents et leurs distances par rapport à la question

SIMILARITY_THRESHOLD = 0.65
# fonction pour vérifier si la meilleure distance est inférieure au seuil de similarité
def is_within_scope(distances: list) -> bool:
    meilleure_distance = distances[0][0]
    return meilleure_distance < SIMILARITY_THRESHOLD # retourne True si la meilleure distance est inférieure au seuil, sinon False

# fonction pour vérifier si la question est dans le périmètre de l'oncologie
def check_scope(question: str):
    results = search_relevant_chunks(question)
    if not is_within_scope(results["distances"]):
        return None  # hors périmètre
    return results  # dans le périmètre, chunks utilisables

# fonction pour construire le prompt à partir de la question et des chunks pertinents
def build_prompt(question: str, chunks: list[str]) -> str:
    contexte = "\n\n".join(chunks)

    prompt = f"""Tu es un assistant spécialisé uniquement en oncologie. Réponds à la question de l'utilisateur en te basant strictement sur le contexte fourni ci-dessous. Si le contexte ne permet pas de répondre à la question, ou si la question ne concerne pas l'oncologie, dis-le clairement plutôt que d'inventer une réponse.

Si la question posée ne porte pas sur l'oncologie (même si des termes médicaux apparaissent dans le contexte), réponds uniquement : "Cette question ne concerne pas l'oncologie."
Si le contexte ne permet pas de répondre à une question qui concerne bien l'oncologie, dis-le clairement plutôt que d'inventer une réponse.
Si la question porte sur un pronostic vital, des chances de survie, ou une inquiétude personnelle sur l'issue d'un cancer, ne donne jamais d'estimation. Réponds avec empathie que seul un médecin ayant accès au dossier complet du patient peut évaluer un pronostic, et encourage la personne à en discuter avec son oncologue traitant.


Contexte :
{contexte}

Question : {question}

Réponse :"""

    return prompt

# fonction pour interroger le LLM avec le prompt construit
def ask_llm(prompt: str) -> str:
    model = genai.GenerativeModel("models/gemini-3.5-flash-lite")
    response = model.generate_content(prompt)
    return response.text
# fonction principale pour répondre à une question en utilisant les chunks pertinents et le LLM
def answer_question(question: str) -> str:
    results = search_relevant_chunks(question)

    if not is_within_scope(results["distances"]):
        return "Cette question sort de mon domaine (oncologie)."

    chunks_texte = results["documents"][0]
    prompt = build_prompt(question, chunks_texte)
    reponse = ask_llm(prompt)

    return reponse
