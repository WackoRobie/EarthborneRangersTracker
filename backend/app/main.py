from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
import app.models  # noqa: F401 — registers all models with Base
from app.seed import seed_reference_data
from app.routers import campaigns, rangers, storylines


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_reference_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Earthborne Rangers Tracker",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(storylines.router)
app.include_router(campaigns.router)
app.include_router(rangers.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
