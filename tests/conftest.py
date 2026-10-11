from fastapi.testclient import TestClient
from app.main import app
import pytest
from sqlalchemy.pool import StaticPool
from app.models.user import User
from app.models.blacklistToken import BlacklistToken
from app.models.document import Document
from app.models.message import Message
from app.models.session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db

engine = create_engine("sqlite://",connect_args={"check_same_thread": False},poolclass=StaticPool,)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
