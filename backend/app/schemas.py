

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Location Schemas

class LocationResponse(BaseModel):
    """Response schema for a random game location."""
    id: int
    lat: float
    lng: float
    country: str
    difficulty: str

    class Config:
        from_attributes = True


# Guess Schemas

class GuessRequest(BaseModel):
    """Request body for submitting a player's guess."""
    round_number: int
    guess_lat: float
    guess_lng: float
    actual_lat: float
    actual_lng: float


class GuessResponse(BaseModel):
    """Response after evaluating a player's guess."""
    distance_km: float
    score: int


# Game Results Schemas

class GameResultResponse(BaseModel):
    """Schema for a single stored game result."""
    id: int
    round_number: int
    guess_lat: float
    guess_lng: float
    actual_lat: float
    actual_lng: float
    distance: float
    score: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
