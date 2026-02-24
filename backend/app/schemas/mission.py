from pydantic import BaseModel, ConfigDict


class MissionCreate(BaseModel):
    name: str
    max_progress: int = 0       # 0 = pass/fail only, 1–3 = trackable steps
    day_started_id: int | None = None   # defaults to current active day if omitted


class MissionUpdate(BaseModel):
    progress: int | None = None
    day_completed_id: int | None = None   # set to mark mission complete


class MissionResponse(BaseModel):
    id: int
    campaign_id: int
    name: str
    day_started_id: int | None = None
    day_completed_id: int | None = None
    progress: int
    max_progress: int

    model_config = ConfigDict(from_attributes=True)
