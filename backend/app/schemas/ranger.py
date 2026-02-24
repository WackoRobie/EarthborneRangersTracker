from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CardRef(BaseModel):
    id: int
    name: str
    card_type: str
    source_set: str
    aspect: str | None = None
    cost: int | None = None
    tags: list[str]
    is_expert: bool

    model_config = ConfigDict(from_attributes=True)


class DeckEntry(BaseModel):
    """A card in the current decklist with its quantity (>1 when un-traded copies remain)."""
    card: CardRef
    quantity: int


class TradeResponse(BaseModel):
    id: int
    day_id: int
    original_card: CardRef
    reward_card: CardRef
    reverted: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Request bodies ---

class RangerCreate(BaseModel):
    name: str
    aspect_card_name: str
    awa: int
    fit: int
    foc: int
    spi: int
    background_set: str       # Artisan | Forager | Shepherd | Traveler
    specialty_set: str        # Artificer | Conciliator | Explorer | Shaper
    personality_card_ids: list[int]      # exactly 4, one per aspect
    background_card_ids: list[int]       # exactly 5, from background_set
    specialty_card_ids: list[int]        # exactly 5, from specialty_set, no roles
    role_card_id: int                    # role card from specialty_set
    outside_interest_card_id: int        # any non-role, non-expert background/specialty card


class TradeCreate(BaseModel):
    day_id: int
    original_card_id: int   # card currently in the ranger's deck
    reward_card_id: int     # card currently in the campaign rewards pool


# --- Responses ---

class RangerResponse(BaseModel):
    id: int
    campaign_id: int
    name: str
    aspect_card_name: str
    awa: int
    fit: int
    foc: int
    spi: int
    background_set: str
    specialty_set: str
    personality_card_ids: list[int]
    background_card_ids: list[int]
    specialty_card_ids: list[int]
    role_card: CardRef
    outside_interest_card: CardRef
    trades: list[TradeResponse] = []
    current_decklist: list[DeckEntry] = []

    model_config = ConfigDict(from_attributes=True)
