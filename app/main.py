from fastapi import FastAPI
from app.routes import auth
from app.routes import admin
from app.routes import chat
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.rate_limiter import limiter

app = FastAPI(title="OncoConseil", description="API backend avec llm", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API OncoConseil"}

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])