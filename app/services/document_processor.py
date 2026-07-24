from typing import List
import google.generativeai as genai
from app.config import settings
from pypdf import PdfReader

genai.configure(api_key=settings.LLM_API_KEY)

# fonction pour découper le texte en morceaux de taille fixe avec chevauchement
def split_into_chunks(text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
    words = text.split()  # découpe le texte en mots
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # avance, en reculant un peu pour le chevauchement
    return chunks

# fonction pour extraire le texte d'un fichier PDF
def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + " "
    return full_text

def generate_embedding(text: str) -> list: # fonction pour générer un vecteur d'embedding à partir d'un texte
    result = genai.embed_content(model="models/gemini-embedding-001", content=text) # utilise le modèle d'embedding pour générer un vecteur d'embedding
    return result["embedding"] # retourne le vecteur d'embedding