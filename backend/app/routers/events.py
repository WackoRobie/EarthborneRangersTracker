from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_campaign_write
from app.models.campaign import Campaign, CampaignDay, NotableEvent
from app.schemas.event import EventCreate, EventResponse

router = APIRouter(prefix="/api/campaigns/{campaign_id}/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
def list_events(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    return campaign.notable_events


@router.post("", response_model=EventResponse, status_code=201)
def create_event(
    campaign_id: int,
    body: EventCreate,
    campaign: Campaign = Depends(require_campaign_write),
    db: Session = Depends(get_db),
):
    day = db.get(CampaignDay, body.day_id)
    if not day or day.campaign_id != campaign_id:
        raise HTTPException(400, "day_id does not belong to this campaign")

    event = NotableEvent(
        campaign_id=campaign_id,
        day_id=body.day_id,
        text=body.text,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=204)
def delete_event(
    campaign_id: int,
    event_id: int,
    campaign: Campaign = Depends(require_campaign_write),
    db: Session = Depends(get_db),
):
    event = db.get(NotableEvent, event_id)
    if not event or event.campaign_id != campaign_id:
        raise HTTPException(404, "Event not found")

    db.delete(event)
    db.commit()
