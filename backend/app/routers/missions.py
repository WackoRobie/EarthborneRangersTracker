from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.campaign import Campaign, CampaignDay, DayStatus, Mission
from app.schemas.mission import MissionCreate, MissionResponse, MissionUpdate

router = APIRouter(prefix="/api/campaigns/{campaign_id}/missions", tags=["missions"])


def _get_campaign_or_404(campaign_id: int, db: Session) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    return campaign


def _active_day_id(campaign: Campaign) -> int | None:
    for day in campaign.days:
        if day.status == DayStatus.active:
            return day.id
    return None


@router.get("", response_model=list[MissionResponse])
def list_missions(campaign_id: int, db: Session = Depends(get_db)):
    campaign = _get_campaign_or_404(campaign_id, db)
    return campaign.missions


@router.post("", response_model=MissionResponse, status_code=201)
def create_mission(campaign_id: int, body: MissionCreate, db: Session = Depends(get_db)):
    campaign = _get_campaign_or_404(campaign_id, db)

    if body.max_progress < 0 or body.max_progress > 3:
        raise HTTPException(400, "max_progress must be between 0 and 3")

    # Default day_started to the current active day
    day_started_id = body.day_started_id
    if day_started_id is None:
        day_started_id = _active_day_id(campaign)

    # Validate day belongs to this campaign if explicitly provided
    if body.day_started_id is not None:
        day = db.get(CampaignDay, body.day_started_id)
        if not day or day.campaign_id != campaign_id:
            raise HTTPException(400, "day_started_id does not belong to this campaign")

    mission = Mission(
        campaign_id=campaign_id,
        name=body.name,
        max_progress=body.max_progress,
        day_started_id=day_started_id,
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission


@router.patch("/{mission_id}", response_model=MissionResponse)
def update_mission(
    campaign_id: int,
    mission_id: int,
    body: MissionUpdate,
    db: Session = Depends(get_db),
):
    _get_campaign_or_404(campaign_id, db)

    mission = db.get(Mission, mission_id)
    if not mission or mission.campaign_id != campaign_id:
        raise HTTPException(404, "Mission not found")

    if body.progress is not None:
        if body.progress < 0 or body.progress > mission.max_progress:
            raise HTTPException(
                400,
                f"progress must be between 0 and {mission.max_progress} for this mission"
            )
        mission.progress = body.progress

    if body.day_completed_id is not None:
        day = db.get(CampaignDay, body.day_completed_id)
        if not day or day.campaign_id != campaign_id:
            raise HTTPException(400, "day_completed_id does not belong to this campaign")
        mission.day_completed_id = body.day_completed_id

    db.commit()
    db.refresh(mission)
    return mission
