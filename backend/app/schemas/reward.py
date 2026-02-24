from pydantic import BaseModel, ConfigDict


class RewardAdd(BaseModel):
    card_name: str
    quantity: int = 1


class RewardResponse(BaseModel):
    id: int
    card_name: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)
