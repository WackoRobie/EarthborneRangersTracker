from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StorylineRef(BaseModel):
    id: int
    name: str
    min_rangers: int
    max_rangers: int

    model_config = ConfigDict(from_attributes=True)


class DayResponse(BaseModel):
    id: int
    day_number: int
    weather: str
    status: str
    location: str | None = None
    path_terrain: str | None = None

    model_config = ConfigDict(from_attributes=True)


# --- Campaign request bodies ---

class CampaignCreate(BaseModel):
    name: str
    storyline_id: int


class CampaignUpdate(BaseModel):
    name: str | None = None
    status: str | None = None


# --- Campaign responses ---

class CampaignResponse(BaseModel):
    """Summary — used in list responses."""
    id: int
    name: str
    status: str
    created_at: datetime
    storyline: StorylineRef
    current_day: DayResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class CampaignDetailResponse(CampaignResponse):
    """Full detail — used for single-campaign responses."""
    days: list[DayResponse] = []
