"""
Game API routes.
Handles location retrieval, guess submission, and results fetching.
"""

import os
import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Location, GameResult
from ..schemas import LocationResponse, GuessRequest, GuessResponse, GameResultResponse
from ..services.geo import haversine_distance, calculate_score, build_streetview_url

router = APIRouter(prefix="/game", tags=["game"])


@router.get("/random-location", response_model=LocationResponse)
def get_random_location(difficulty: str = "all", db: Session = Depends(get_db)):
    """
    Return a random location from the seeded database.
    Optionally filter by difficulty: easy | medium | hard | all
    """
    query = db.query(Location)

    if difficulty != "all":
        query = query.filter(Location.difficulty == difficulty)

    locations = query.all()

    if not locations:
        raise HTTPException(status_code=404, detail="No locations found")

    location = random.choice(locations)
    return location


@router.get("/streetview-url")
def get_streetview_url(lat: float, lng: float):
    """
    Generate a Google Street View Static API URL for a given coordinate.
    The API key is read from environment variables.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="Google Maps API key not configured")

    url = build_streetview_url(lat, lng, api_key)
    return {"url": url}


@router.post("/submit-guess", response_model=GuessResponse)
def submit_guess(guess: GuessRequest, db: Session = Depends(get_db)):
    """
    Accept a player's location guess, compute distance and score,
    and persist the result to the database.
    """
    # Calculate distance using Haversine formula
    distance_km = haversine_distance(
        guess.actual_lat, guess.actual_lng,
        guess.guess_lat, guess.guess_lng
    )

    # Compute score based on distance
    score = calculate_score(distance_km)

    # Persist the round result to the database
    result = GameResult(
        round_number=guess.round_number,
        guess_lat=guess.guess_lat,
        guess_lng=guess.guess_lng,
        actual_lat=guess.actual_lat,
        actual_lng=guess.actual_lng,
        distance=distance_km,
        score=score,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return GuessResponse(distance_km=distance_km, score=score)


@router.get("/results", response_model=list[GameResultResponse])
def get_results(limit: int = 50, db: Session = Depends(get_db)):
    """
    Return the most recent game results stored in SQLite.
    Ordered by most recently played.
    """
    results = (
        db.query(GameResult)
        .order_by(GameResult.created_at.desc())
        .limit(limit)
        .all()
    )
    return results


@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    """
    Return aggregated leaderboard stats — top scoring game sessions
    grouped by sets of 3 rounds.
    """
    results = db.query(GameResult).order_by(GameResult.created_at.desc()).all()

    # Group results into sessions of 3 rounds
    sessions = []
    for i in range(0, len(results) - 2, 3):
        session_rounds = results[i:i + 3]
        if len(session_rounds) == 3:
            total_score = sum(r.score for r in session_rounds)
            avg_distance = sum(r.distance for r in session_rounds) / 3
            sessions.append({
                "played_at": session_rounds[0].created_at,
                "total_score": total_score,
                "avg_distance_km": round(avg_distance, 1),
                "rounds": [
                    {
                        "round": r.round_number,
                        "score": r.score,
                        "distance_km": r.distance,
                    }
                    for r in session_rounds
                ],
            })

    # Sort by total score descending
    sessions.sort(key=lambda s: s["total_score"], reverse=True)
    return sessions[:10]  # Top 10
