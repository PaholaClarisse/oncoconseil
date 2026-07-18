from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.auth import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate, UserOut, UserLogin
from datetime import datetime
from app.models.user import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
         # 1. Vérifier si email existe
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email déjà utilisé")

        # 2. Hacher le mot de passe
        hashed_pwd = hash_password(user.password)

        # 3. Préparer le document
        new_user = User(
            name=user.name,
            email=user.email,
            hashed_password=hashed_pwd,
            created_at=datetime.utcnow()
        )

        # 4. Insérer dans postgresql
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    
        return new_user

@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # 1. Vérifier si l'utilisateur existe
    existing_user = db.query(User).filter(User.email == user.email).first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")

    # 2. Vérifier le mot de passe
    if not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mot de passe incorrect")

    # 3. Générer un token JWT
    access_token = create_access_token(data={"sub": existing_user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

