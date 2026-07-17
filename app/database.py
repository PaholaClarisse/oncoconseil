from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.POSTGRE_URL) # créer un moteur de base de données en utilisant l'URL de connexion PostgreSQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # créer une session locale pour interagir avec la base de données
Base = declarative_base() # créer une classe de base pour les modèles SQLAlchemy