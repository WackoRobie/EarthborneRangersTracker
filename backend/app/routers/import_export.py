from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.campaign import Campaign, CampaignDay, CampaignReward, Mission, NotableEvent
from app.models.card import Card
from app.models.ranger import Ranger, RangerTrade
from app.models.storyline import Storyline
from app.models.user import User
from app.schemas.import_export import ImportBody

router = APIRouter(prefix="/api/campaigns", tags=["import_export"])


# ── Export ────────────────────────────────────────────────────────────────────

@router.get("/{campaign_id}/export")
def export_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")

    # Build card_id → name lookup
    all_cards = db.query(Card).all()
    card_name_of = {c.id: c.name for c in all_cards}

    # Build day_id → day_number lookup
    day_number_of = {d.id: d.day_number for d in campaign.days}

    days = [
        {
            "day_number": d.day_number,
            "weather": d.weather,
            "status": d.status,
            "location": d.location,
            "path_terrain": d.path_terrain,
        }
        for d in campaign.days
    ]

    rangers = []
    for r in campaign.rangers:
        trades = [
            {
                "day_number": day_number_of[t.day_id],
                "original_card_name": card_name_of[t.original_card_id],
                "reward_card_name": card_name_of[t.reward_card_id],
                "reverted": t.reverted,
            }
            for t in r.trades
        ]
        rangers.append({
            "name": r.name,
            "aspect_card_name": r.aspect_card_name,
            "awa": r.awa,
            "fit": r.fit,
            "foc": r.foc,
            "spi": r.spi,
            "background_set": r.background_set,
            "specialty_set": r.specialty_set,
            "personality_card_names": [card_name_of[cid] for cid in r.personality_card_ids],
            "background_card_names": [card_name_of[cid] for cid in r.background_card_ids],
            "specialty_card_names": [card_name_of[cid] for cid in r.specialty_card_ids],
            "role_card_name": card_name_of[r.role_card_id],
            "outside_interest_card_name": card_name_of[r.outside_interest_card_id],
            "trades": trades,
        })

    missions = [
        {
            "name": m.name,
            "max_progress": m.max_progress,
            "progress": m.progress,
            "day_started_number": day_number_of.get(m.day_started_id) if m.day_started_id else None,
            "day_completed_number": day_number_of.get(m.day_completed_id) if m.day_completed_id else None,
        }
        for m in campaign.missions
    ]

    events = [
        {"text": e.text, "day_number": day_number_of[e.day_id]}
        for e in campaign.notable_events
    ]

    rewards = [
        {"card_name": rw.card_name, "quantity": rw.quantity}
        for rw in campaign.rewards
    ]

    payload = {
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "campaign": {
            "name": campaign.name,
            "status": campaign.status,
            "storyline_name": campaign.storyline.name,
            "days": days,
            "rangers": rangers,
            "missions": missions,
            "events": events,
            "rewards": rewards,
        },
    }

    return JSONResponse(content=payload)


# ── Import ────────────────────────────────────────────────────────────────────

@router.post("/import", status_code=201)
def import_campaign(
    body: ImportBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = body.campaign

    # 1. Look up storyline by name
    storyline = db.query(Storyline).filter_by(name=data.storyline_name).first()
    if not storyline:
        raise HTTPException(422, f"Storyline '{data.storyline_name}' not found on this server")

    # 2. Build card_name → Card lookup
    all_cards = db.query(Card).all()
    card_by_name = {c.name: c for c in all_cards}

    # 3. Validate all card names referenced by rangers and trades
    unknown: set[str] = set()
    for r in data.rangers:
        for name in r.personality_card_names + r.background_card_names + r.specialty_card_names:
            if name not in card_by_name:
                unknown.add(name)
        for name in (r.role_card_name, r.outside_interest_card_name):
            if name not in card_by_name:
                unknown.add(name)
        for t in r.trades:
            for name in (t.original_card_name, t.reward_card_name):
                if name not in card_by_name:
                    unknown.add(name)

    if unknown:
        raise HTTPException(422, f"Unknown card names: {', '.join(sorted(unknown))}")

    # 4. Create campaign
    campaign = Campaign(
        name=data.name,
        storyline_id=storyline.id,
        status=data.status,
        owner_id=current_user.id,
    )
    db.add(campaign)
    db.flush()

    # 5. Create days
    for d in data.days:
        db.add(CampaignDay(
            campaign_id=campaign.id,
            day_number=d.day_number,
            weather=d.weather,
            status=d.status,
            location=d.location,
            path_terrain=d.path_terrain,
        ))
    db.flush()

    # 6. Build day_number → day_id lookup
    day_id_of = {
        d.day_number: d.id
        for d in db.query(CampaignDay).filter_by(campaign_id=campaign.id).all()
    }

    # 7. Create rangers and their trades
    for r in data.rangers:
        ranger = Ranger(
            campaign_id=campaign.id,
            name=r.name,
            aspect_card_name=r.aspect_card_name,
            awa=r.awa,
            fit=r.fit,
            foc=r.foc,
            spi=r.spi,
            background_set=r.background_set,
            specialty_set=r.specialty_set,
            personality_card_ids=[card_by_name[n].id for n in r.personality_card_names],
            background_card_ids=[card_by_name[n].id for n in r.background_card_names],
            specialty_card_ids=[card_by_name[n].id for n in r.specialty_card_names],
            role_card_id=card_by_name[r.role_card_name].id,
            outside_interest_card_id=card_by_name[r.outside_interest_card_name].id,
        )
        db.add(ranger)
        db.flush()

        for t in r.trades:
            db.add(RangerTrade(
                ranger_id=ranger.id,
                day_id=day_id_of[t.day_number],
                original_card_id=card_by_name[t.original_card_name].id,
                reward_card_id=card_by_name[t.reward_card_name].id,
                reverted=t.reverted,
            ))

    # 8. Create missions
    for m in data.missions:
        db.add(Mission(
            campaign_id=campaign.id,
            name=m.name,
            max_progress=m.max_progress,
            progress=m.progress,
            day_started_id=day_id_of.get(m.day_started_number) if m.day_started_number is not None else None,
            day_completed_id=day_id_of.get(m.day_completed_number) if m.day_completed_number is not None else None,
        ))

    # 9. Create events
    for e in data.events:
        db.add(NotableEvent(
            campaign_id=campaign.id,
            day_id=day_id_of[e.day_number],
            text=e.text,
        ))

    # 10. Create rewards
    for rw in data.rewards:
        db.add(CampaignReward(
            campaign_id=campaign.id,
            card_name=rw.card_name,
            quantity=rw.quantity,
        ))

    db.commit()
    return {"campaign_id": campaign.id}
