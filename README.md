# Earthborne Rangers Tracker

A web-based campaign tracker for [Earthborne Rangers](https://earthbornerangers.com/), a cooperative card game with persistent campaigns.

## What It Does

Earthborne Rangers campaigns span multiple play sessions across 30 days of in-game time. Between sessions, rangers swap cards with a shared rewards pool, missions progress, and the story evolves. Keeping track of all of this on paper is error-prone — this app handles it.

Key features:
- **Campaign management** — run multiple independent campaigns simultaneously
- **Deck tracking** — maintains each ranger's exact deck composition across trades so players can physically rebuild decks before each session
- **Session setup** — surfaces weather, destination location, and path terrain at the start of each day
- **Mission tracking** — log missions with progress steps (0–3) and mark them complete
- **Rewards pool** — manage the campaign-wide card pool and record trades between rangers with full independent reversion support
- **Notable events** — free-form text log for memorable moments
- **Campaign export / import** — back up and restore campaigns as JSON
- **Multi-user accounts** — each campaign has an owner; write access can be granted to collaborators

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| Backend | Python 3.12 + FastAPI |
| Database | PostgreSQL 16 |
| Auth | JWT (Bearer tokens) |
| Reverse proxy | nginx (SSL termination) |
| Local dev | Docker Compose |

## Running Locally

**Prerequisites:** Docker and Docker Compose.

```bash
git clone git@github.com:WackoRobie/EarthborneRangersTracker.git
cd EarthborneRangersTracker
docker compose up --build
```

The app will be available at `http://localhost` (or `https://localhost` if SSL certs are configured).

The backend API is available at `/api/` and auto-documented at `/api/docs`.

## Running Tests

```bash
# Create the test database (first time only, or after docker compose down -v)
docker compose exec db psql -U rangers -d earthborne -c "CREATE DATABASE earthborne_test OWNER rangers;"

# Run the backend test suite
docker compose exec backend pytest tests/ -v
```

75 backend tests, 27 frontend tests.

## API Overview

All endpoints except `/api/auth/register` and `/api/auth/login` require a Bearer token.

| Resource | Prefix |
|---|---|
| Auth | `/api/auth` |
| Campaigns | `/api/campaigns` |
| Days | `/api/campaigns/{id}/days` |
| Rangers | `/api/campaigns/{id}/rangers` |
| Missions | `/api/campaigns/{id}/missions` |
| Rewards pool | `/api/campaigns/{id}/rewards` |
| Notable events | `/api/campaigns/{id}/events` |
| Access (collaborators) | `/api/campaigns/{id}/access` |
| Export / Import | `/api/campaigns/{id}/export`, `/api/campaigns/import` |

Full interactive docs are served by FastAPI at `/api/docs`.

## Project Structure

```
earthborne_rangers/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + router registration
│   │   ├── auth.py          # JWT helpers + get_current_user dependency
│   │   ├── dependencies.py  # Per-campaign authorization dependencies
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── routers/         # One module per domain entity
│   │   └── schemas/         # Pydantic request/response schemas
│   └── tests/
├── frontend/
│   └── src/
└── docker-compose.yml
```
