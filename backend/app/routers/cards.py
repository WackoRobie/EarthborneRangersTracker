from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.card import Card
from app.schemas.card import CardResponse

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.get("", response_model=list[CardResponse])
def list_cards(
    card_type: str | None = None,
    source_set: str | None = None,
    db: Session = Depends(get_db),
):
    """List cards, optionally filtered by card_type and/or source_set.

    Examples:
      /api/cards?card_type=personality
      /api/cards?card_type=background&source_set=Artisan
      /api/cards?card_type=role&source_set=Explorer
    """
    q = db.query(Card)
    if card_type:
        q = q.filter(Card.card_type == card_type)
    if source_set:
        q = q.filter(Card.source_set == source_set)
    return q.order_by(Card.source_set, Card.name).all()
