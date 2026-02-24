from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventCreate(BaseModel):
    text: str
    day_id: int


class EventResponse(BaseModel):
    id: int
    campaign_id: int
    day_id: int
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
