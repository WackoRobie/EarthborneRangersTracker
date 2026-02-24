import enum

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class CardType(str, enum.Enum):
    personality = "personality"
    background = "background"
    specialty = "specialty"
    role = "role"


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # Where the card comes from
    card_type = Column(String, nullable=False)   # CardType enum value
    source_set = Column(String, nullable=False)  # AWA/FIT/FOC/SPI | Artisan/Forager/… | Artificer/…

    # Energy aspect and cost to play (NULL for role cards which start in play)
    aspect = Column(String, nullable=True)       # AWA | FIT | FOC | SPI
    cost = Column(Integer, nullable=True)        # 0–3; NULL = variable (X cost)

    # Type tags parsed from printed card text (e.g. ["Gear", "Tool", "Tech"])
    tags = Column(JSONB, nullable=False, default=list)

    # Expert cards cannot be chosen as outside interest
    is_expert = Column(Boolean, nullable=False, default=False)
