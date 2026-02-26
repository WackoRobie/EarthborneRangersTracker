from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.dependencies import require_campaign_write
from app.models.campaign import Campaign, CampaignDay, CampaignStatus, DayStatus
from app.models.storyline import Storyline, StorylineDayPreset
from app.models.user import User
from app.schemas.campaign import (
    CampaignCreate,
    CampaignDetailResponse,
    CampaignResponse,
    CampaignUpdate,
)

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


def _active_day(campaign: Campaign) -> CampaignDay | None:
    return next((d for d in campaign.days if d.status == DayStatus.active), None)


@router.get("", response_model=list[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    for c in campaigns:
        c.current_day = _active_day(c)
    return campaigns


@router.post("", response_model=CampaignDetailResponse, status_code=201)
def create_campaign(
    body: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    storyline = db.get(Storyline, body.storyline_id)
    if not storyline:
        raise HTTPException(status_code=404, detail="Storyline not found")

    campaign = Campaign(name=body.name, storyline_id=body.storyline_id, owner_id=current_user.id)
    db.add(campaign)
    db.flush()

    presets = (
        db.query(StorylineDayPreset)
        .filter_by(storyline_id=body.storyline_id)
        .order_by(StorylineDayPreset.day_number)
        .all()
    )

    if not presets:
        raise HTTPException(status_code=400, detail="Storyline has no day presets configured")

    days = [
        CampaignDay(
            campaign_id=campaign.id,
            day_number=p.day_number,
            weather=p.weather,
            # Day 1 is immediately active; all others wait their turn
            status=DayStatus.active if i == 0 else DayStatus.upcoming,
            location=p.default_location,
            path_terrain=p.default_path_terrain,
        )
        for i, p in enumerate(presets)
    ]
    db.bulk_save_objects(days)
    db.commit()
    db.refresh(campaign)

    campaign.current_day = _active_day(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.current_day = _active_day(campaign)
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: int,
    body: CampaignUpdate,
    campaign: Campaign = Depends(require_campaign_write),
    db: Session = Depends(get_db),
):
    if body.name is not None:
        campaign.name = body.name

    if body.status is not None:
        if body.status not in (CampaignStatus.active, CampaignStatus.completed, CampaignStatus.archived):
            raise HTTPException(status_code=400, detail="status must be 'active', 'completed', or 'archived'")
        campaign.status = body.status

    db.commit()
    db.refresh(campaign)
    campaign.current_day = _active_day(campaign)
    return campaign


@router.delete("/{campaign_id}", status_code=204)
def delete_campaign(
    campaign_id: int,
    campaign: Campaign = Depends(require_campaign_write),
    db: Session = Depends(get_db),
):
    db.delete(campaign)
    db.commit()
