from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.campaign import Campaign, CampaignDay, CampaignStatus, DayStatus
from app.schemas.campaign import DayResponse

router = APIRouter(prefix="/api/campaigns/{campaign_id}/days", tags=["days"])


class DayCloseRequest(BaseModel):
    location: str
    path_terrain: str


def _get_campaign_or_404(campaign_id: int, db: Session) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    return campaign


@router.get("/{day_id}", response_model=DayResponse)
def get_day(campaign_id: int, day_id: int, db: Session = Depends(get_db)):
    _get_campaign_or_404(campaign_id, db)
    day = db.get(CampaignDay, day_id)
    if not day or day.campaign_id != campaign_id:
        raise HTTPException(404, "Day not found")
    return day


@router.post("/{day_id}/close", response_model=DayResponse)
def close_day(
    campaign_id: int,
    day_id: int,
    body: DayCloseRequest,
    db: Session = Depends(get_db),
):
    """Close the active day and advance the campaign to the next day.

    - Marks the current day as completed.
    - Sets location and path_terrain on Day N+1 (surfaced at next session start).
    - Activates Day N+1.
    - If this is the final day, marks the campaign as completed instead.
    """
    campaign = _get_campaign_or_404(campaign_id, db)

    day = db.get(CampaignDay, day_id)
    if not day or day.campaign_id != campaign_id:
        raise HTTPException(404, "Day not found")
    if day.status != DayStatus.active:
        raise HTTPException(400, f"Day {day.day_number} is not active (current status: {day.status})")

    day.status = DayStatus.completed

    next_day = (
        db.query(CampaignDay)
        .filter_by(campaign_id=campaign_id, day_number=day.day_number + 1)
        .first()
    )

    if next_day:
        next_day.status = DayStatus.active
        next_day.location = body.location
        next_day.path_terrain = body.path_terrain
    else:
        # Final day — campaign is complete
        campaign.status = CampaignStatus.completed

    db.commit()
    db.refresh(day)
    return day
