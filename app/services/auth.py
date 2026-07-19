from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.database import SessionLocal
from sqlalchemy.orm import Session
from app.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# fonction de hachage de mot de passe 
def hash_password(password:str)->str:
    pwd = password.encode("utf-8")[:72] # tronquer le mot de passe à 72 octets pour éviter les problèmes avec bcrypt
    pwd = pwd.decode("utf-8", "ignore") # décoder le mot de passe en UTF-8 en ignorant les erreurs de décodage
    return pwd_context.hash(pwd) # hacher le mot de passe tronqué à 72 octets

# verifier le mot de passe haché avec le mot de passe en clair
def verify_password(plain_password:str, hashed_password:str)->bool:
    return pwd_context.verify(plain_password, hashed_password)


# fonction pour générer un token JWT
def create_access_token(data: dict)->str:
    to_encode = data.copy()
    expire  = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) # définir la date d'expiration du token
    to_encode.update({"exp": expire}) # ajouter la date d'expiration au dictionnaire des données à encoder
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM) # encoder le dictionnaire des données avec la clé secrète et l'algorithme spécifié
    return encoded_jwt # retourner le token JWT encodé

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> dict:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token d'authentification invalide",headers={"WWW-Authenticate": "Bearer"},)
    try:
        # décoder le token JWT pour obtenir les informations de l'utilisateur
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # récupérer l'ID de l'utilisateur à partir du token
        id: str = payload.get("sub")
        # vérifier si l'ID est présent dans le token, sinon lever une exception
        if id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # récupérer l'utilisateur à partir de la base de données en utilisant l'ID extrait du token
    user = db.query(User).filter(User.id == int(id)).first()
    # vérifier si l'utilisateur existe dans la base de données, sinon lever une exception
    if user is None:
        raise credentials_exception
        # retourner l'utilisateur trouvé dans la base de données
    return user
