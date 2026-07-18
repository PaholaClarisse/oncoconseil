from fastapi import FastAPI
from app.routes import auth

app = FastAPI(title="OncoConseil", description="API backend avec llm", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API OncoConseil"}

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])