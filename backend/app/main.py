
from .seed import seed_database
from .routes import game
from .models import Base
from .database import engine
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks: create tables and seed locations."""
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(
    title="GeoGuessr MVP API",
    description="Backend API for a GeoGuessr-style geography guessing game.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow Streamlit frontend (localhost:8501) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register game routes under /game prefix
app.include_router(game.router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "GeoGuessr MVP API is running 🌍"}


@app.get("/health")
def health():
    return {"status": "healthy"}
