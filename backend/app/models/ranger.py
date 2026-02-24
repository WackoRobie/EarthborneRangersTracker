from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Ranger(Base):
    """A player character belonging to a campaign.

    Deck foundation fields store lists of card IDs (JSONB arrays).
    The current decklist is derived at read time:
        starting deck  −  traded-away originals  +  received rewards (non-reverted trades)
    """

    __tablename__ = "rangers"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    name = Column(String, nullable=False)

    # Aspect card (chosen first; determines the four stat ratings)
    aspect_card_name = Column(String, nullable=False)
    awa = Column(Integer, nullable=False)
    fit = Column(Integer, nullable=False)
    foc = Column(Integer, nullable=False)
    spi = Column(Integer, nullable=False)

    # Deck foundation — set at creation, never changed
    # Each personality card is included ×2 in the deck (4 cards → 8 in deck)
    personality_card_ids = Column(JSONB, nullable=False)   # [id, id, id, id]

    # Background set name and the 5 chosen cards (×2 each → 10 in deck)
    background_set = Column(String, nullable=False)        # Artisan | Forager | Shepherd | Traveler
    background_card_ids = Column(JSONB, nullable=False)    # [id, id, id, id, id]

    # Specialty set name and the 5 chosen cards (×2 each → 10 in deck)
    specialty_set = Column(String, nullable=False)         # Artificer | Conciliator | Explorer | Shaper
    specialty_card_ids = Column(JSONB, nullable=False)     # [id, id, id, id, id]

    # Role card starts in play, NOT in deck
    role_card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)

    # Outside interest card (×2 in deck → 2 cards)
    outside_interest_card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="rangers")
    role_card = relationship("Card", foreign_keys=[role_card_id])
    outside_interest_card = relationship("Card", foreign_keys=[outside_interest_card_id])
    trades = relationship("RangerTrade", back_populates="ranger", cascade="all, delete-orphan")


class RangerTrade(Base):
    """Records a single card swap made at day close.

    Each trade is independent and can be reverted individually:
    - Reverting restores original_card to the deck
    - Reverting returns reward_card to the campaign rewards pool
    - A card traded away (original or reward) goes back to the campaign pool
    """

    __tablename__ = "ranger_trades"

    id = Column(Integer, primary_key=True)
    ranger_id = Column(Integer, ForeignKey("rangers.id"), nullable=False)
    day_id = Column(Integer, ForeignKey("campaign_days.id"), nullable=False)
    original_card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    reward_card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    reverted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    ranger = relationship("Ranger", back_populates="trades")
    day = relationship("CampaignDay", back_populates="trades")
    original_card = relationship("Card", foreign_keys=[original_card_id])
    reward_card = relationship("Card", foreign_keys=[reward_card_id])
