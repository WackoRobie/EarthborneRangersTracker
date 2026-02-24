from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Storyline(Base):
    __tablename__ = "storylines"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    min_rangers = Column(Integer, nullable=False, default=1)
    max_rangers = Column(Integer, nullable=False, default=4)

    day_presets = relationship(
        "StorylineDayPreset",
        back_populates="storyline",
        order_by="StorylineDayPreset.day_number",
    )
    campaigns = relationship("Campaign", back_populates="storyline")


class StorylineDayPreset(Base):
    """Preset data for each day in a storyline — weather is fixed; location/path
    are only set for Day 1 (the campaign starting point).  All subsequent days'
    location and path are recorded at the close of the previous day."""

    __tablename__ = "storyline_day_presets"

    id = Column(Integer, primary_key=True)
    storyline_id = Column(Integer, ForeignKey("storylines.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    weather = Column(String, nullable=False)

    # Day 1 starting position (set by the storyline rules, not player choice)
    default_location = Column(String, nullable=True)
    default_path_terrain = Column(String, nullable=True)

    storyline = relationship("Storyline", back_populates="day_presets")
