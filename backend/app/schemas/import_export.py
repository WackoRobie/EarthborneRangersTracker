from typing import Annotated, Literal

from pydantic import BaseModel, Field

# Reusable constrained types
_CardName = Annotated[str, Field(min_length=1, max_length=200)]
_DayNumber = Annotated[int, Field(ge=1, le=30)]
_Stat = Annotated[int, Field(ge=0, le=10)]


class ImportTrade(BaseModel):
    day_number: _DayNumber
    original_card_name: _CardName
    reward_card_name: _CardName
    reverted: bool = False


class ImportRanger(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=200)]
    aspect_card_name: _CardName
    awa: _Stat
    fit: _Stat
    foc: _Stat
    spi: _Stat
    background_set: Annotated[str, Field(min_length=1, max_length=100)]
    specialty_set: Annotated[str, Field(min_length=1, max_length=100)]
    personality_card_names: Annotated[list[_CardName], Field(max_length=4)]
    background_card_names: Annotated[list[_CardName], Field(max_length=5)]
    specialty_card_names: Annotated[list[_CardName], Field(max_length=5)]
    role_card_name: _CardName
    outside_interest_card_name: _CardName
    trades: Annotated[list[ImportTrade], Field(default=[], max_length=200)]


class ImportDay(BaseModel):
    day_number: _DayNumber
    weather: Annotated[str, Field(min_length=1, max_length=100)]
    status: Literal["upcoming", "active", "completed"] = "upcoming"
    location: Annotated[str | None, Field(max_length=200)] = None
    path_terrain: Annotated[str | None, Field(max_length=200)] = None


class ImportMission(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=200)]
    max_progress: Annotated[int, Field(ge=0, le=3)] = 0
    progress: Annotated[int, Field(ge=0, le=3)] = 0
    day_started_number: _DayNumber | None = None
    day_completed_number: _DayNumber | None = None


class ImportEvent(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=5000)]
    day_number: _DayNumber


class ImportReward(BaseModel):
    card_name: _CardName
    quantity: Annotated[int, Field(ge=1, le=999)]


class ImportCampaign(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=200)]
    status: Literal["active", "completed", "archived"] = "active"
    storyline_name: Annotated[str, Field(min_length=1, max_length=200)]
    days: Annotated[list[ImportDay], Field(default=[], max_length=31)]
    rangers: Annotated[list[ImportRanger], Field(default=[], max_length=4)]
    missions: Annotated[list[ImportMission], Field(default=[], max_length=200)]
    events: Annotated[list[ImportEvent], Field(default=[], max_length=1000)]
    rewards: Annotated[list[ImportReward], Field(default=[], max_length=500)]


class ImportBody(BaseModel):
    version: Annotated[int, Field(ge=1, le=1)]
    campaign: ImportCampaign
