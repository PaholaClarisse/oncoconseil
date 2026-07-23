from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document
from app.services.document_processor import extract_text_from_pdf, split_into_chunks, generate_embedding
from app.vector_db import collection
import shutil

router = APIRouter()

@router.post("/documents")
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    texte = extract_text_from_pdf(temp_path)
    chunks = split_into_chunks(texte)

    new_document = Document(name=file.filename, nombre_chunks=len(chunks))
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    for i, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)
        collection.add(
            ids=[f"{new_document.id}_{i}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"document_id": new_document.id}]
        )

    return {"message": "Document indexé avec succès", "document_id": new_document.id, "nombre_chunks": len(chunks)}