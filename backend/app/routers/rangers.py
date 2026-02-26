from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_campaign_write
from app.models.campaign import Campaign, CampaignDay, CampaignReward
from app.models.card import Card
from app.models.ranger import Ranger, RangerTrade
from app.schemas.ranger import (
    CardRef,
    DeckEntry,
    RangerCreate,
    RangerResponse,
    TradeCreate,
    TradeResponse,
)

router = APIRouter(prefix="/api/campaigns/{campaign_id}/rangers", tags=["rangers"])

_VALID_BACKGROUNDS = ("Artisan", "Forager", "Shepherd", "Traveler")
_VALID_SPECIALTIES = ("Artificer", "Conciliator", "Explorer", "Shaper")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_campaign_or_404(campaign_id: int, db: Session) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


def _get_ranger_or_404(campaign_id: int, ranger_id: int, db: Session) -> Ranger:
    ranger = db.get(Ranger, ranger_id)
    if not ranger or ranger.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Ranger not found")
    return ranger


def _compute_decklist(ranger: Ranger, db: Session) -> list[DeckEntry]:
    """Derive the ranger's current deck from starting cards plus trade history.

    Starting deck: each selected card ×2.
    Each non-reverted trade: −1 original, +1 reward.
    """
    deck: Counter = Counter()

    for cid in ranger.personality_card_ids:
        deck[cid] += 2
    for cid in ranger.background_card_ids:
        deck[cid] += 2
    for cid in ranger.specialty_card_ids:
        deck[cid] += 2
    deck[ranger.outside_interest_card_id] += 2

    for trade in ranger.trades:
        if not trade.reverted:
            deck[trade.original_card_id] -= 1
            deck[trade.reward_card_id] += 1

    live_ids = {cid for cid, qty in deck.items() if qty > 0}
    card_map = {c.id: c for c in db.query(Card).filter(Card.id.in_(live_ids)).all()}

    return [
        DeckEntry(card=CardRef.model_validate(card_map[cid]), quantity=qty)
        for cid, qty in sorted(deck.items(), key=lambda x: card_map[x[0]].name if x[0] in card_map else "")
        if qty > 0
    ]


def _campaign_cards_in_use(campaign_id: int, db: Session) -> set[int]:
    """Return all card IDs already selected by any ranger in the campaign."""
    rangers = db.query(Ranger).filter_by(campaign_id=campaign_id).all()
    in_use: set[int] = set()
    for r in rangers:
        in_use.update(r.personality_card_ids)
        in_use.update(r.background_card_ids)
        in_use.update(r.specialty_card_ids)
        in_use.add(r.outside_interest_card_id)
        in_use.add(r.role_card_id)
    return in_use


def _validate_ranger_cards(body: RangerCreate, db: Session, campaign_id: int) -> None:
    """Validate all card selections against the card library and rules."""

    # Personality: exactly 4, one per aspect
    if len(body.personality_card_ids) != 4:
        raise HTTPException(400, "Exactly 4 personality cards required")

    p_cards = db.query(Card).filter(Card.id.in_(body.personality_card_ids)).all()
    if len(p_cards) != len(body.personality_card_ids):
        raise HTTPException(400, "One or more personality card IDs not found")

    aspects_seen = set()
    for c in p_cards:
        if c.card_type != "personality":
            raise HTTPException(400, f"'{c.name}' is not a personality card")
        if c.source_set in aspects_seen:
            raise HTTPException(400, f"Duplicate aspect {c.source_set} — choose one personality card per aspect")
        aspects_seen.add(c.source_set)

    if aspects_seen != {"AWA", "FIT", "FOC", "SPI"}:
        raise HTTPException(400, "Must choose one personality card for each aspect: AWA, FIT, FOC, SPI")

    # Background: exactly 5, all from the chosen set
    if body.background_set not in _VALID_BACKGROUNDS:
        raise HTTPException(400, f"background_set must be one of {_VALID_BACKGROUNDS}")

    if len(body.background_card_ids) != 5:
        raise HTTPException(400, "Exactly 5 background cards required")

    bg_cards = db.query(Card).filter(Card.id.in_(body.background_card_ids)).all()
    if len(bg_cards) != len(body.background_card_ids):
        raise HTTPException(400, "One or more background card IDs not found")

    for c in bg_cards:
        if c.card_type != "background" or c.source_set != body.background_set:
            raise HTTPException(400, f"'{c.name}' is not a {body.background_set} background card")

    # Specialty: exactly 5, all from the chosen set, no role cards
    if body.specialty_set not in _VALID_SPECIALTIES:
        raise HTTPException(400, f"specialty_set must be one of {_VALID_SPECIALTIES}")

    if len(body.specialty_card_ids) != 5:
        raise HTTPException(400, "Exactly 5 specialty cards required")

    sp_cards = db.query(Card).filter(Card.id.in_(body.specialty_card_ids)).all()
    if len(sp_cards) != len(body.specialty_card_ids):
        raise HTTPException(400, "One or more specialty card IDs not found")

    for c in sp_cards:
        if c.card_type == "role":
            raise HTTPException(400, f"'{c.name}' is a role card and cannot be added to the deck")
        if c.card_type != "specialty" or c.source_set != body.specialty_set:
            raise HTTPException(400, f"'{c.name}' is not a {body.specialty_set} specialty card")

    # Role card: from the chosen specialty set
    role_card = db.get(Card, body.role_card_id)
    if not role_card:
        raise HTTPException(400, "Role card not found")
    if role_card.card_type != "role" or role_card.source_set != body.specialty_set:
        raise HTTPException(400, f"'{role_card.name}' is not a {body.specialty_set} role card")

    # No duplicate card IDs within background or specialty selections
    if len(set(body.background_card_ids)) != len(body.background_card_ids):
        raise HTTPException(400, "Duplicate cards in background selection")
    if len(set(body.specialty_card_ids)) != len(body.specialty_card_ids):
        raise HTTPException(400, "Duplicate cards in specialty selection")

    # Outside interest: any background or specialty card, not a role, not expert,
    # and not already chosen for background or specialty
    already_chosen = set(body.background_card_ids) | set(body.specialty_card_ids)
    if body.outside_interest_card_id in already_chosen:
        raise HTTPException(400, "Outside interest card is already chosen as a background or specialty card")

    oi_card = db.get(Card, body.outside_interest_card_id)
    if not oi_card:
        raise HTTPException(400, "Outside interest card not found")
    if oi_card.card_type not in ("background", "specialty"):
        raise HTTPException(400, "Outside interest must be a background or specialty card")
    if oi_card.is_expert:
        raise HTTPException(400, f"'{oi_card.name}' has the Expert trait and cannot be chosen as outside interest")

    # Campaign-wide uniqueness: no card can be held by more than one ranger
    all_new_ids = (
        set(body.personality_card_ids)
        | set(body.background_card_ids)
        | set(body.specialty_card_ids)
        | {body.outside_interest_card_id, body.role_card_id}
    )
    in_use = _campaign_cards_in_use(campaign_id, db)
    conflicts = all_new_ids & in_use
    if conflicts:
        names = [
            c.name for c in db.query(Card).filter(Card.id.in_(conflicts)).all()
        ]
        raise HTTPException(
            400,
            f"The following cards are already selected by another ranger in this campaign: {', '.join(names)}"
        )


def _adjust_pool(campaign_id: int, card_id: int, delta: int, db: Session) -> None:
    """Add or remove a card from the campaign rewards pool."""
    entry = db.query(CampaignReward).filter_by(campaign_id=campaign_id, card_id=card_id).first()
    if entry:
        entry.quantity += delta
        if entry.quantity <= 0:
            db.delete(entry)
    elif delta > 0:
        db.add(CampaignReward(campaign_id=campaign_id, card_id=card_id, quantity=delta))


# ---------------------------------------------------------------------------
# Ranger endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[RangerResponse])
def list_rangers(campaign_id: int, db: Session = Depends(get_db)):
    campaign = _get_campaign_or_404(campaign_id, db)
    for ranger in campaign.rangers:
        ranger.current_decklist = _compute_decklist(ranger, db)
    return campaign.rangers


@router.post("", response_model=RangerResponse, status_code=201)
def create_ranger(
    campaign_id: int,
    body: RangerCreate,
    campaign: Campaign = Depends(require_campaign_write),
    db: Session = Depends(get_db),
):
    if len(campaign.rangers) >= campaign.storyline.max_rangers:
        raise HTTPException(
            400,
            f"Campaign already has the maximum of {campaign.storyline.max_rangers} rangers"
        )

    _validate_ranger_cards(body, db, campaign_id)

    ranger = Ranger(
        campaign_id=campaign_id,
        name=body.name,
        aspect_card_name=body.aspect_card_name,
        awa=body.awa,
        fit=body.fit,
        foc=body.foc,
        spi=body.spi,
        background_set=body.background_set,
        specialty_set=body.specialty_set,
        personality_card_ids=body.personality_card_ids,
        background_card_ids=body.background_card_ids,
        specialty_card_ids=body.specialty_card_ids,
        role_card_id=body.role_card_id,
        outside_interest_card_id=body.outside_interest_card_id,
    )
    db.add(ranger)
    db.commit()
    db.refresh(ranger)

    ranger.current_decklist = _compute_decklist(ranger, db)
    return ranger


@router.get("/{ranger_id}", response_model=RangerResponse)
def get_ranger(campaign_id: int, ranger_id: int, db: Session = Depends(get_db)):
    ranger = _get_ranger_or_404(campaign_id, ranger_id, db)
    ranger.current_decklist = _compute_decklist(ranger, db)
    return ranger


# ---------------------------------------------------------------------------
# Trade endpoints
# ---------------------------------------------------------------------------

@router.post("/{ranger_id}/trades", response_model=TradeResponse, status_code=201)
def create_trade(
    campaign_id: int,
    ranger_id: int,
    body: TradeCreate,
    campaign: Campaign = Depends(require_campaign_write),
    db: Session = Depends(get_db),
):
    ranger = _get_ranger_or_404(campaign_id, ranger_id, db)

    day = db.get(CampaignDay, body.day_id)
    if not day or day.campaign_id != campaign_id:
        raise HTTPException(400, "Day not found in this campaign")

    # Original card must be in the ranger's current deck
    deck = _compute_decklist(ranger, db)
    deck_card_ids = {entry.card.id for entry in deck}
    if body.original_card_id not in deck_card_ids:
        raise HTTPException(400, "Original card is not in the ranger's current deck")

    # Reward card must be available in the campaign rewards pool
    pool_entry = db.query(CampaignReward).filter_by(
        campaign_id=campaign_id, card_id=body.reward_card_id
    ).first()
    if not pool_entry or pool_entry.quantity < 1:
        raise HTTPException(400, "Reward card is not available in the campaign rewards pool")

    trade = RangerTrade(
        ranger_id=ranger_id,
        day_id=body.day_id,
        original_card_id=body.original_card_id,
        reward_card_id=body.reward_card_id,
    )
    db.add(trade)

    # Reward leaves pool; original enters pool
    _adjust_pool(campaign_id, body.reward_card_id, -1, db)
    _adjust_pool(campaign_id, body.original_card_id, +1, db)

    db.commit()
    db.refresh(trade)
    return trade


@router.post("/{ranger_id}/trades/{trade_id}/revert", response_model=TradeResponse)
def revert_trade(
    campaign_id: int,
    ranger_id: int,
    trade_id: int,
    campaign: Campaign = Depends(require_campaign_write),
    db: Session = Depends(get_db),
):
    _get_ranger_or_404(campaign_id, ranger_id, db)

    trade = db.get(RangerTrade, trade_id)
    if not trade or trade.ranger_id != ranger_id:
        raise HTTPException(404, "Trade not found")
    if trade.reverted:
        raise HTTPException(400, "Trade is already reverted")

    trade.reverted = True

    # Original returns to deck (leave pool); reward returns to pool
    _adjust_pool(campaign_id, trade.original_card_id, -1, db)
    _adjust_pool(campaign_id, trade.reward_card_id, +1, db)

    db.commit()
    db.refresh(trade)
    return trade
