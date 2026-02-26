import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class CampaignStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    archived = "archived"


class DayStatus(str, enum.Enum):
    upcoming = "upcoming"
    active = "active"
    completed = "completed"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    storyline_id = Column(Integer, ForeignKey("storylines.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, nullable=False, default=CampaignStatus.active)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    storyline = relationship("Storyline", back_populates="campaigns")
    owner = relationship("User", foreign_keys=[owner_id])
    collaborators = relationship("CampaignCollaborator", back_populates="campaign", cascade="all, delete-orphan")
    days = relationship("CampaignDay", back_populates="campaign", order_by="CampaignDay.day_number", cascade="all, delete-orphan")
    rangers = relationship("Ranger", back_populates="campaign", cascade="all, delete-orphan")
    rewards = relationship("CampaignReward", back_populates="campaign", cascade="all, delete-orphan")
    missions = relationship("Mission", back_populates="campaign", cascade="all, delete-orphan")
    notable_events = relationship("NotableEvent", back_populates="campaign", cascade="all, delete-orphan")


class CampaignReward(Base):
    """A card currently available in the campaign-wide rewards pool.

    card_name stores a free-form card name (physical card from the game).
    card_id is reserved for future use when pool entries are linked to the card library.
    """

    __tablename__ = "campaign_rewards"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    card_name = Column(String, nullable=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)

    campaign = relationship("Campaign", back_populates="rewards")
    card = relationship("Card")


class CampaignDay(Base):
    """One play session within a campaign.

    location and path_terrain describe where the rangers are *heading* —
    they are recorded at the close of the previous day and surfaced at the
    start of this day.  Day 1 values are copied from the storyline preset."""

    __tablename__ = "campaign_days"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    weather = Column(String, nullable=False)
    status = Column(String, nullable=False, default=DayStatus.upcoming)
    location = Column(String, nullable=True)
    path_terrain = Column(String, nullable=True)

    campaign = relationship("Campaign", back_populates="days")
    notable_events = relationship("NotableEvent", back_populates="day")
    trades = relationship("RangerTrade", back_populates="day")
    missions_started = relationship("Mission", foreign_keys="Mission.day_started_id", back_populates="day_started")
    missions_completed = relationship("Mission", foreign_keys="Mission.day_completed_id", back_populates="day_completed")


class Mission(Base):
    """A trackable campaign objective.

    max_progress=0 means the mission is pass/fail only (no intermediate steps).
    max_progress=1–3 means there are that many trackable progress steps."""

    __tablename__ = "missions"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    name = Column(String, nullable=False)
    day_started_id = Column(Integer, ForeignKey("campaign_days.id"), nullable=True)
    day_completed_id = Column(Integer, ForeignKey("campaign_days.id"), nullable=True)
    progress = Column(Integer, nullable=False, default=0)
    max_progress = Column(Integer, nullable=False, default=0)

    campaign = relationship("Campaign", back_populates="missions")
    day_started = relationship("CampaignDay", foreign_keys=[day_started_id], back_populates="missions_started")
    day_completed = relationship("CampaignDay", foreign_keys=[day_completed_id], back_populates="missions_completed")


class NotableEvent(Base):
    __tablename__ = "notable_events"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    day_id = Column(Integer, ForeignKey("campaign_days.id"), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="notable_events")
    day = relationship("CampaignDay", back_populates="notable_events")
