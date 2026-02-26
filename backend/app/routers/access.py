from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_campaign_owner
from app.models.access import CampaignCollaborator
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.access import CollaboratorAdd, CollaboratorResponse

router = APIRouter(prefix="/api/campaigns/{campaign_id}/access", tags=["access"])


@router.get("", response_model=list[CollaboratorResponse])
def list_collaborators(
    campaign_id: int,
    campaign: Campaign = Depends(require_campaign_owner),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(CampaignCollaborator, User)
        .join(User, CampaignCollaborator.user_id == User.id)
        .filter(CampaignCollaborator.campaign_id == campaign_id)
        .all()
    )
    return [
        CollaboratorResponse(user_id=c.user_id, username=u.username, added_at=c.added_at)
        for c, u in rows
    ]


@router.post("", response_model=CollaboratorResponse, status_code=201)
def add_collaborator(
    campaign_id: int,
    body: CollaboratorAdd,
    campaign: Campaign = Depends(require_campaign_owner),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter_by(username=body.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = (
        db.query(CampaignCollaborator)
        .filter_by(campaign_id=campaign_id, user_id=user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="User is already a collaborator")

    collab = CampaignCollaborator(campaign_id=campaign_id, user_id=user.id)
    db.add(collab)
    db.commit()
    db.refresh(collab)

    return CollaboratorResponse(user_id=user.id, username=user.username, added_at=collab.added_at)


@router.delete("/{user_id}", status_code=204)
def remove_collaborator(
    campaign_id: int,
    user_id: int,
    campaign: Campaign = Depends(require_campaign_owner),
    db: Session = Depends(get_db),
):
    collab = (
        db.query(CampaignCollaborator)
        .filter_by(campaign_id=campaign_id, user_id=user_id)
        .first()
    )
    if not collab:
        raise HTTPException(status_code=404, detail="Collaborator not found")

    db.delete(collab)
    db.commit()
