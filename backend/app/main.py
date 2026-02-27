from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import get_current_user
from app.config import settings
from app.database import engine, Base, SessionLocal
import app.models  # noqa: F401 — registers all models with Base
from app.seed import seed_reference_data
from app.routers import access, auth, campaigns, cards, days, events, import_export, missions, rangers, rewards, storylines


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
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Auth router — no authentication required (login/register are public)
app.include_router(auth.router)

# All other routers require a valid JWT
_auth = [Depends(get_current_user)]
app.include_router(storylines.router, dependencies=_auth)
app.include_router(campaigns.router, dependencies=_auth)
app.include_router(days.router, dependencies=_auth)
app.include_router(rangers.router, dependencies=_auth)
app.include_router(missions.router, dependencies=_auth)
app.include_router(events.router, dependencies=_auth)
app.include_router(rewards.router, dependencies=_auth)
app.include_router(cards.router, dependencies=_auth)
app.include_router(import_export.router, dependencies=_auth)
app.include_router(access.router, dependencies=_auth)


@app.get("/api/health")
def health():
    return {"status": "ok"}
