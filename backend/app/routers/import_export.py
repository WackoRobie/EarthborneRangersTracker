from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.campaign import Campaign, CampaignDay, CampaignReward, DayStatus, Mission, NotableEvent
from app.models.card import Card
from app.models.ranger import Ranger, RangerTrade
from app.models.storyline import Storyline
from app.models.user import User

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
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Basic validation
    if "version" not in body or "campaign" not in body:
        raise HTTPException(422, "Invalid export file: missing 'version' or 'campaign'")

    data = body["campaign"]

    # 2. Look up storyline by name
    storyline = db.query(Storyline).filter_by(name=data["storyline_name"]).first()
    if not storyline:
        raise HTTPException(422, f"Storyline '{data['storyline_name']}' not found on this server")

    # 3. Build card_name → Card lookup
    all_cards = db.query(Card).all()
    card_by_name = {c.name: c for c in all_cards}

    # 4. Validate all card names referenced by rangers and trades
    unknown: set[str] = set()
    for r in data.get("rangers", []):
        for name in r.get("personality_card_names", []):
            if name not in card_by_name:
                unknown.add(name)
        for name in r.get("background_card_names", []):
            if name not in card_by_name:
                unknown.add(name)
        for name in r.get("specialty_card_names", []):
            if name not in card_by_name:
                unknown.add(name)
        role = r.get("role_card_name")
        if role and role not in card_by_name:
            unknown.add(role)
        oi = r.get("outside_interest_card_name")
        if oi and oi not in card_by_name:
            unknown.add(oi)
        for t in r.get("trades", []):
            orig = t.get("original_card_name")
            if orig and orig not in card_by_name:
                unknown.add(orig)
            reward = t.get("reward_card_name")
            if reward and reward not in card_by_name:
                unknown.add(reward)

    if unknown:
        raise HTTPException(422, f"Unknown card names: {', '.join(sorted(unknown))}")

    # 5. Create campaign
    campaign = Campaign(
        name=data["name"],
        storyline_id=storyline.id,
        status=data.get("status", "active"),
        owner_id=current_user.id,
    )
    db.add(campaign)
    db.flush()

    # 6. Create days
    for d in data.get("days", []):
        db.add(CampaignDay(
            campaign_id=campaign.id,
            day_number=d["day_number"],
            weather=d["weather"],
            status=d.get("status", DayStatus.upcoming),
            location=d.get("location"),
            path_terrain=d.get("path_terrain"),
        ))
    db.flush()

    # 7. Build day_number → day_id lookup
    day_id_of = {
        d.day_number: d.id
        for d in db.query(CampaignDay).filter_by(campaign_id=campaign.id).all()
    }

    # 8. Create rangers and their trades
    for r in data.get("rangers", []):
        ranger = Ranger(
            campaign_id=campaign.id,
            name=r["name"],
            aspect_card_name=r["aspect_card_name"],
            awa=r["awa"],
            fit=r["fit"],
            foc=r["foc"],
            spi=r["spi"],
            background_set=r["background_set"],
            specialty_set=r["specialty_set"],
            personality_card_ids=[card_by_name[n].id for n in r["personality_card_names"]],
            background_card_ids=[card_by_name[n].id for n in r["background_card_names"]],
            specialty_card_ids=[card_by_name[n].id for n in r["specialty_card_names"]],
            role_card_id=card_by_name[r["role_card_name"]].id,
            outside_interest_card_id=card_by_name[r["outside_interest_card_name"]].id,
        )
        db.add(ranger)
        db.flush()

        for t in r.get("trades", []):
            db.add(RangerTrade(
                ranger_id=ranger.id,
                day_id=day_id_of[t["day_number"]],
                original_card_id=card_by_name[t["original_card_name"]].id,
                reward_card_id=card_by_name[t["reward_card_name"]].id,
                reverted=t.get("reverted", False),
            ))

    # 9. Create missions
    for m in data.get("missions", []):
        started_num = m.get("day_started_number")
        completed_num = m.get("day_completed_number")
        db.add(Mission(
            campaign_id=campaign.id,
            name=m["name"],
            max_progress=m.get("max_progress", 0),
            progress=m.get("progress", 0),
            day_started_id=day_id_of.get(started_num) if started_num is not None else None,
            day_completed_id=day_id_of.get(completed_num) if completed_num is not None else None,
        ))

    # 10. Create events
    for e in data.get("events", []):
        db.add(NotableEvent(
            campaign_id=campaign.id,
            day_id=day_id_of[e["day_number"]],
            text=e["text"],
        ))

    # 11. Create rewards (free-form card names pass through directly)
    for rw in data.get("rewards", []):
        if rw.get("card_name") and rw.get("quantity", 0) > 0:
            db.add(CampaignReward(
                campaign_id=campaign.id,
                card_name=rw["card_name"],
                quantity=rw["quantity"],
            ))

    db.commit()
    return {"campaign_id": campaign.id}
