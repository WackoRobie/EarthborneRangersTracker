from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.access import CampaignCollaborator
from app.models.campaign import Campaign
from app.models.user import User


def require_campaign_write(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Campaign:
    """Allow access if: campaign has no owner (legacy), user is owner, or user is collaborator."""
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.owner_id is None:
        return campaign

    if campaign.owner_id == current_user.id:
        return campaign

    collab = (
        db.query(CampaignCollaborator)
        .filter_by(campaign_id=campaign_id, user_id=current_user.id)
        .first()
    )
    if collab:
        return campaign

    raise HTTPException(status_code=403, detail="Access denied")


def require_campaign_owner(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Campaign:
    """Allow access only to the campaign owner."""
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return campaign
