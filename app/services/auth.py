from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
