from fastapi import FastAPI
from app.routes import auth
from app.routes import admin

app = FastAPI(title="OncoConseil", description="API backend avec llm", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API OncoConseil"}

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])