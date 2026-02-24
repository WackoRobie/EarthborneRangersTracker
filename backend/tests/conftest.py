"""
Shared fixtures for the backend test suite.

Tests run inside the backend container against a separate 'earthborne_test'
database so the production data volume is never touched.

Run with:
    docker compose exec backend pytest tests/ -v
"""

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

import app.models  # noqa: F401 — registers all models with Base
from app.database import Base, get_db
from app.main import app
from app.models.card import Card
from app.models.storyline import Storyline
from app.seed import seed_reference_data

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://rangers:rangers@db:5432/earthborne_test",
)


# ---------------------------------------------------------------------------
# Session-scoped: engine, schema creation, reference data seed
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=eng)
    _seed(eng)
    yield eng
    Base.metadata.drop_all(bind=eng)


def _seed(engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        seed_reference_data(db)
    finally:
        db.close()


@pytest.fixture(scope="session")
def card_ids(engine):
    """Dict mapping card name → id for all seeded cards."""
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        return {c.name: c.id for c in db.query(Card).all()}
    finally:
        db.close()


@pytest.fixture(scope="session")
def storyline_id(engine):
    """ID of the seeded 'Lore of the Valley' storyline."""
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        s = db.query(Storyline).filter_by(name="Lore of the Valley").first()
        return s.id
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Function-scoped: HTTP client + per-test data cleanup
# ---------------------------------------------------------------------------

@pytest.fixture
def client(engine):
    """
    TestClient with get_db overridden to use the test database.
    A new session is created for each request, mirroring production behaviour.
    """
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # Do NOT use TestClient as a context manager — that triggers lifespan,
    # which would run create_all + seed against the test DB a second time.
    c = TestClient(app, raise_server_exceptions=True)
    yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clean_campaigns(engine):
    """Truncate all campaign-derived data after every test."""
    yield
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE campaigns CASCADE"))
        conn.commit()


# ---------------------------------------------------------------------------
# Convenience campaign / ranger payload fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def campaign(client, storyline_id):
    """Create and return a test campaign dict."""
    r = client.post("/api/campaigns", json={"name": "Test Run", "storyline_id": storyline_id})
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def ranger_payload(card_ids):
    """
    A fully valid RangerCreate payload using known seeded card names.

    Personality : Insightful (AWA), Passionate (FIT), Meticulous (FOC), Persuasive (SPI)
    Background  : Artisan — 5 non-expert cards
    Specialty   : Artificer — 5 non-expert specialty cards + Masterful Engineer (role)
    Outside int.: Familiar Ground (Forager background, non-expert)
    """
    return {
        "name": "Aria",
        "aspect_card_name": "Sun Warden",
        "awa": 2,
        "fit": 3,
        "foc": 2,
        "spi": 3,
        "background_set": "Artisan",
        "specialty_set": "Artificer",
        "personality_card_ids": [
            card_ids["Insightful"],
            card_ids["Passionate"],
            card_ids["Meticulous"],
            card_ids["Persuasive"],
        ],
        "background_card_ids": [
            card_ids["Universal Power Cells"],
            card_ids["Functional Replica"],
            card_ids["The Right Tool"],
            card_ids["Pocketed Belt Pouch"],
            card_ids["The Mother of Invention"],
        ],
        "specialty_card_ids": [
            card_ids["Ferinodex"],
            card_ids["Carbonforged Cable"],
            card_ids["Dayhowler"],
            card_ids["Trail Markers"],
            card_ids["Spiderpad Gloves"],
        ],
        "role_card_id": card_ids["Masterful Engineer"],
        "outside_interest_card_id": card_ids["Familiar Ground"],
    }
