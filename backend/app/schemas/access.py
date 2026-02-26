from datetime import datetime

from pydantic import BaseModel


class CollaboratorAdd(BaseModel):
    username: str


class CollaboratorResponse(BaseModel):
    user_id: int
    username: str
    added_at: datetime
