# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Web-based campaign tracker for **Earthborne Rangers**, a cooperative card game with persistent campaigns. The app is being designed through an ongoing conversation with the user — refer to the conversation history for requirements that have not yet been coded.

## Architecture

**Stack:**
- Frontend: React 18 (Vite)
- Backend: Python 3.12 + FastAPI
- Database: PostgreSQL 16
- Local dev: Docker Compose

**Deployment path:**
1. Current: Single AWS Lightsail instance, Docker Compose
2. Target: AWS serverless (Lambda + API Gateway + Aurora Serverless or DynamoDB)
3. Possible: iOS app (requires API-first design — already in place)

**Folder structure:**
```
earthborne_rangers/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI app, startup, CORS
│   │   ├── config.py      # Settings via pydantic-settings
│   │   ├── database.py    # SQLAlchemy engine, Base, get_db()
│   │   ├── models/        # SQLAlchemy ORM models
│   │   └── routers/       # Route modules (one per domain entity)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   └── App.jsx
│   ├── Dockerfile
│   ├── vite.config.js
│   └── package.json
├── docker-compose.yml
└── CLAUDE.md
```

**API conventions:**
- All backend routes are prefixed `/api/` (e.g. `/api/health`, `/api/campaigns`)
- Vite dev server proxies `/api/*` to the backend container
- This prefix makes nginx routing and future Lambda path-based routing straightforward

## Domain Model

### Storyline
A narrative arc (e.g. *Lore of the Valley*). Defines the campaign length and the preset weather for each day.
- Name
- Days: ordered list of day presets, each with a weather value
- Weather values are storyline-specific (not a global enum); *Lore of the Valley* uses: A Perfect Day, Downpour, Howling Winds

### Campaign
An independent playthrough of a Storyline. Multiple campaigns can run simultaneously.
- Name
- Storyline (FK)
- Status: active | completed
- Rewards pool: campaign-wide list of card names available for trades
- Notable events: free-form text log

### Day
One play session within a Campaign.
- Campaign (FK)
- Day number (1–30 for *Lore of the Valley*)
- Weather (preset from Storyline, surfaced at session start)
- Status: upcoming | active | completed
- Location
- Path Terrain

### Mission
A trackable objective within a Campaign.
- Campaign (FK)
- Name
- Day started (FK → Day)
- Day completed (FK → Day, nullable)
- Progress: integer 0–3 (actual steps completed)
- Max progress: integer 0–3 (0 = pass/fail only, defined per mission)

### Ranger
A player character belonging to a Campaign. Created at campaign start; deck evolves across days.

**Identity & stats:**
- Name
- Campaign (FK)
- Aspect card name (chosen first; determines the four numeric ratings)
- AWA, FIT, FOC, SPI (integers from the chosen aspect card)

**Deck foundation (set at creation, all cards identified by printed name):**
- Personality: 4 card names (one per aspect — AWA, FIT, FOC, SPI); each added ×2 to deck → 8 cards
- Background set: Artisan | Forager | Shepherd | Traveler
- Background cards: 5 card names from the chosen set; each added ×2 → 10 cards
- Specialty set: Artificer | Conciliator | Explorer | Shaper
- Specialty cards: 5 card names from the chosen set; each added ×2 → 10 cards
- Outside interest: 1 card name (any specialty/background card, not role/expert); added ×2 → 2 cards
- Role card: 1 card name (from specialty); NOT in deck — starts in play

**Starting deck size: 30 cards** (8 + 10 + 10 + 2). Deck may grow via acquired cards.

**Trade mechanics:**
- Trades are recorded as independent pairs: original card ↔ reward card
- Any card traded away (original or reward) returns to the campaign rewards pool
- Individual trades can be reverted independently: original card returns to deck, reward card returns to campaign pool
- Cards in the campaign pool can be re-traded to any ranger, including the one who returned them
- Current decklist = starting deck − traded-away originals + received rewards (non-reverted trades)

## Session Flow

Each play session maps to one Day. The app supports three phases:

### 1. Session Start (read-only, surfaced from previous day close)
- Weather for this day (preset by storyline)
- Destination location and path type (recorded at close of previous day)
- Ongoing missions with current progress

### 2. During Session
- Add notable events (free-form text entries)
- Update mission progress / mark missions complete
- Add earned rewards to the campaign rewards pool

### 3. Day Close
- Record destination location and path type for the **next** session
- Execute deck swaps: rangers trade cards from their deck for cards in the rewards pool
  - Traded-away cards return to the campaign pool
  - Each trade is recorded as an independent pair (original ↔ reward) for reversion
- Day is marked complete; Day N+1 becomes the active day

**Day 1 note:** Location and path type for Day 1 are preset by the Storyline (no previous day close).

## Key App Responsibilities

1. Create and manage multiple independent campaigns
2. Track ranger deck composition so players can physically rebuild decks before each session
3. Surface session setup info (weather, location, path terrain) at the start of each day
4. Log outcomes at the close of each day (missions, notable events)
5. Manage the campaign rewards pool and ranger trades with full independent reversion support

## Outstanding Questions

### Campaign & Rangers
- [x] **Campaign log fields** — resolved. See Session Flow below.

### World & Setup
- [x] **Ranger stats** — fixed at creation; AWA/FIT/FOC/SPI do not change over the campaign.
- [ ] **Storyline expansions** — how do expansion storylines differ structurally from the base *Lore of the Valley*? Any data that needs special handling?

## Future TODOs

### Rewards pool → card library integration
The rewards pool currently stores card names as free-form text. When the card library grows to cover all earnable cards, the pool should be upgraded so each entry can optionally link to a `Card` row (the `card_id` FK already exists in `campaign_rewards`, currently unused).

Once that link exists, the day-close trade recording can be fully restored:
- Trades need to match pool entries by card ID (not just name) so that `RangerTrade` can record the precise card that moved and pool quantities are reliably decremented/incremented on revert.
- The `TradeCreate` request body should accept a `reward_pool_entry_id` so the backend can look up the card from the linked pool entry rather than requiring the client to supply a raw `card_id`.

## Constraints by Storyline

| Storyline | Max days | Min rangers | Max rangers | Weather types |
|---|---|---|---|---|
| Lore of the Valley | 30 | 1 | 4 | A Perfect Day, Downpour, Howling Winds |
