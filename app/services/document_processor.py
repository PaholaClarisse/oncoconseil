from typing import List

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

from pypdf import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + " "
    return full_text

import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.LLM_API_KEY)

def generate_embedding(text: str) -> list:
    result = genai.embed_content(model="models/gemini-embedding-001", content=text)
    return result["embedding"]