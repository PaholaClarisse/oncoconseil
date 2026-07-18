from sqlalchemy import Column, Integer, String, DateTidme, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # cle primaire auto-incrementée
    name = Column(String(50), nullable=False) # nom de l'utilisateur, obligatoire
    email = Column(String(100), unique=True, index=True, nullable=False) # l'email de l'utilisateur, doit être unique et indexé pour des recherches rapides
    hashed_password = Column(String(255), nullable=False) # le mot de passe haché de l'utilisateur, obligatoire
    created_at = Column(DateTime(timezone=True), server_default =func.now()) # l'heure de création de l'utilisateur, par défaut la date et l'heure actuelles
