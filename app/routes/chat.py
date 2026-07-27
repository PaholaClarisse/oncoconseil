from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.schemas.chat import ChatRequest
from app.models.message import Message, MessageRole
from app.models.session import Session 
from app.schemas.chat import ChatRequest
from app.services.chat_service import answer_question
from app.services.auth import get_current_user
from app.models.user import User
from typing import List
from app.schemas.session import SessionOut
from app.schemas.message import MessageOut

router = APIRouter()

@router.post("/ask")
def ask_question(request: ChatRequest, db: DBSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # creer ou reutiliser une session existante pour l'utilisateur
    if request.session_id is None:
        new_session = Session(user_id=current_user.id, title= request.question[:50])  # Utiliser les 50 premiers caractères de la question comme titre
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        session = new_session

    else:
        session= db.query(Session).filter(Session.id == request.session_id).first()
        if session is None:
            raise HTTPException(status_code=404, detail="Session introuvable")

    # Persister la question de l'utilisateur
    user_message = Message(session_id=session.id, role=MessageRole.USER, content=request.question)
    db.add(user_message)
    db.commit()

    # Obtenir la réponse via le pipeline RAG
    reponse_texte = answer_question(request.question)

    # Persister la réponse
    assistant_message = Message(session_id=session.id, role=MessageRole.ASSISTANT, content=reponse_texte)
    db.add(assistant_message)
    db.commit()

    return {
        "session_id": session.id,
        "response": reponse_texte
    }

@router.get("/history", response_model=List[SessionOut])
def get_chat_history(current_user: User = Depends(get_current_user),db: DBSession = Depends(get_db)):
    sessions = db.query(Session).filter(Session.user_id == current_user.id).order_by(Session.created_at.desc()).all()
    return sessions
from app.schemas.message import MessageOut

@router.get("/history/{session_id}", response_model=List[MessageOut])
def get_session_messages(session_id: int,current_user: User = Depends(get_current_user),db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()

    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session introuvable")

    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    return messages