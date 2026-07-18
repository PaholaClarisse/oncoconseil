from dotenv import load_dotenv # telecharger les varables d'environnement depuis le fichier .env
import os

load_dotenv() # charger les variables d'environnement depuis le fichier .env
class Settings:
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))  # Valeur par défaut si la variable d'environnement n'est pas définie
    SECRET_KEY:str = os.getenv("SECRET_KEY") # secret key pour la génération du token JWT
    ALGORITHM:str = os.getenv("ALGORITHM") # algorithme utilisé pour le token JWT 
    ACCESS_TOKEN_EXPIRE_MINUTES:int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))  # Valeur par défaut si la variable d'environnement n'est pas définie
    LLM_API_KEY:str = os.getenv("LLM_API_KEY") # clé API pour l'accès au modèle de langage (LLM)
    POSTGRE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}" # URL de connexion à la base de données PostgreSQL

settings = Settings()