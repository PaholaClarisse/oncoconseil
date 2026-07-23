from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document
from app.services.document_processor import extract_text_from_pdf, split_into_chunks, generate_embedding
from app.vector_db import collection
import shutil
from app.services.auth import get_current_user
from app.models.user import User
from app.schemas.document import DocumentOut

router = APIRouter()

@router.post("/documents")
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

    try:
        for i, chunk in enumerate(chunks):
            embedding = generate_embedding(chunk)
            collection.add(
                ids=[f"{new_document.id}_{i}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"document_id": new_document.id}]
            )
    except Exception as e:
        # Si l'indexation échoue en cours de route, on annule tout :
        # on retire le Document PostgreSQL ET les chunks déjà ajoutés dans ChromaDB
        db.delete(new_document)
        db.commit()
        collection.delete(where={"document_id": new_document.id})
        raise HTTPException(status_code=500, detail=f"Échec de l'indexation : {str(e)}")

    return {
        "message": "Document indexé avec succès",
        "document_id": new_document.id,
        "nombre_chunks": len(chunks)
    }
""" def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
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

    return {"message": "Document indexé avec succès", "document_id": new_document.id, "nombre_chunks": len(chunks)}"""

@router.get("/documents", response_model=list[DocumentOut])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    documents = db.query(Document).all()
    return documents

@router.delete("/documents/{document_id}")
def delete_document(document_id: int,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")

    # 1. Supprimer les chunks correspondants dans ChromaDB
    collection.delete(where={"document_id": document_id})

    # 2. Supprimer l'entrée PostgreSQL
    db.delete(document)
    db.commit()

    return {"message": "Document supprimé avec succès"}