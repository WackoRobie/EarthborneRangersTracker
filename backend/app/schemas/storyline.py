from pydantic import BaseModel, ConfigDict


class DayPresetResponse(BaseModel):
    day_number: int
    weather: str

    model_config = ConfigDict(from_attributes=True)


class StorylineResponse(BaseModel):
    id: int
    name: str
    min_rangers: int
    max_rangers: int
    day_presets: list[DayPresetResponse] = []

    model_config = ConfigDict(from_attributes=True)
