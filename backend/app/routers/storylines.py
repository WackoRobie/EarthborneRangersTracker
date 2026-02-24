from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.storyline import Storyline
from app.schemas.storyline import StorylineResponse

router = APIRouter(prefix="/api/storylines", tags=["storylines"])


@router.get("", response_model=list[StorylineResponse])
def list_storylines(db: Session = Depends(get_db)):
    return db.query(Storyline).order_by(Storyline.name).all()
