from pydantic import BaseModel, ConfigDict

from app.schemas.card import CardResponse


class RewardAdd(BaseModel):
    card_id: int
    quantity: int = 1


class RewardResponse(BaseModel):
    id: int
    card_id: int
    card: CardResponse
    quantity: int

    model_config = ConfigDict(from_attributes=True)
