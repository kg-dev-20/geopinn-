

from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from .database import Base


class Location(Base):
    """
    Seeded geographic locations used for gameplay.
    Each location is a point on Earth with country metadata.
    """
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    country = Column(String, nullable=False)
    difficulty = Column(String, default="medium")  # easy | medium | hard


class GameResult(Base):
    """
    Stores results for each round played by the user.
    One row per round submission.
    """
    __tablename__ = "game_results"

    id = Column(Integer, primary_key=True, index=True)
    round_number = Column(Integer, nullable=False)
    guess_lat = Column(Float, nullable=False)
    guess_lng = Column(Float, nullable=False)
    actual_lat = Column(Float, nullable=False)
    actual_lng = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)        # Distance in kilometers
    score = Column(Integer, nullable=False)          # Score for this round
    created_at = Column(DateTime(timezone=True), server_default=func.now())
