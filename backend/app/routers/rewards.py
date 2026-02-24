from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.campaign import Campaign, CampaignReward
from app.models.card import Card
from app.schemas.reward import RewardAdd, RewardResponse

router = APIRouter(prefix="/api/campaigns/{campaign_id}/rewards", tags=["rewards"])


def _get_campaign_or_404(campaign_id: int, db: Session) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    return campaign


@router.get("", response_model=list[RewardResponse])
def list_rewards(campaign_id: int, db: Session = Depends(get_db)):
    _get_campaign_or_404(campaign_id, db)
    return (
        db.query(CampaignReward)
        .filter_by(campaign_id=campaign_id)
        .all()
    )


@router.post("", response_model=RewardResponse, status_code=201)
def add_reward(campaign_id: int, body: RewardAdd, db: Session = Depends(get_db)):
    """Add a card to the campaign rewards pool (earned during a session)."""
    _get_campaign_or_404(campaign_id, db)

    if body.quantity < 1:
        raise HTTPException(400, "quantity must be at least 1")

    card = db.get(Card, body.card_id)
    if not card:
        raise HTTPException(404, "Card not found")

    entry = db.query(CampaignReward).filter_by(
        campaign_id=campaign_id, card_id=body.card_id
    ).first()

    if entry:
        entry.quantity += body.quantity
    else:
        entry = CampaignReward(
            campaign_id=campaign_id,
            card_id=body.card_id,
            quantity=body.quantity,
        )
        db.add(entry)

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{reward_id}", status_code=204)
def remove_reward(campaign_id: int, reward_id: int, db: Session = Depends(get_db)):
    """Remove a card from the campaign rewards pool."""
    _get_campaign_or_404(campaign_id, db)

    entry = db.get(CampaignReward, reward_id)
    if not entry or entry.campaign_id != campaign_id:
        raise HTTPException(404, "Reward entry not found")

    db.delete(entry)
    db.commit()
