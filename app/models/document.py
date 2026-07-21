from sqlalchemy import Column, Integer, String, func, DateTime
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # cle primaire auto-incrementée
    name = Column(String(100), nullable=False) # nom du document, obligatoire
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # l'heure de création du document, par défaut la date et l'heure actuelles
    nombre_chunks = Column(Integer, nullable=False) # nombre de chunks du document, obligatoire