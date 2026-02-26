from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_campaign_write
from app.models.campaign import Campaign, CampaignReward
from app.schemas.reward import RewardAdd, RewardResponse

router = APIRouter(prefix="/api/campaigns/{campaign_id}/rewards", tags=["rewards"])


@router.get("", response_model=list[RewardResponse])
def list_rewards(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    return (
        db.query(CampaignReward)
        .filter_by(campaign_id=campaign_id)
        .order_by(CampaignReward.card_name)
        .all()
    )


@router.post("", response_model=RewardResponse, status_code=201)
def add_reward(
    campaign_id: int,
    body: RewardAdd,
    campaign: Campaign = Depends(require_campaign_write),
    db: Session = Depends(get_db),
):
    """Add a card to the campaign rewards pool by name."""
    if not body.card_name.strip():
        raise HTTPException(400, "card_name must not be empty")
    if body.quantity < 1:
        raise HTTPException(400, "quantity must be at least 1")

    card_name = body.card_name.strip()

    entry = db.query(CampaignReward).filter_by(
        campaign_id=campaign_id, card_name=card_name
    ).first()

    if entry:
        entry.quantity += body.quantity
    else:
        entry = CampaignReward(
            campaign_id=campaign_id,
            card_name=card_name,
            quantity=body.quantity,
        )
        db.add(entry)

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{reward_id}", status_code=204)
def remove_reward(
    campaign_id: int,
    reward_id: int,
    campaign: Campaign = Depends(require_campaign_write),
    db: Session = Depends(get_db),
):
    """Remove a card from the campaign rewards pool."""
    entry = db.get(CampaignReward, reward_id)
    if not entry or entry.campaign_id != campaign_id:
        raise HTTPException(404, "Reward entry not found")

    db.delete(entry)
    db.commit()
