from pydantic import BaseModel, ConfigDict


class CardResponse(BaseModel):
    id: int
    name: str
    card_type: str
    source_set: str
    aspect: str | None = None
    cost: int | None = None
    tags: list[str]
    is_expert: bool

    model_config = ConfigDict(from_attributes=True)
