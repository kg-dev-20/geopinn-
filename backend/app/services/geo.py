"""
Geographic utility service.
Contains Haversine distance calculation and score computation.
"""

import math


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth
    using the Haversine formula.

    Args:
        lat1, lng1: Coordinates of point 1 (degrees)
        lat2, lng2: Coordinates of point 2 (degrees)

    Returns:
        Distance in kilometers (rounded to 2 decimal places)
    """
    R = 6371  # Earth's radius in kilometers

    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    # Haversine formula
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return round(distance, 2)


def calculate_score(distance_km: float) -> int:
    """
    Calculate score based on distance from the actual location.
    Uses an exponential decay model — closer guesses earn significantly more.

    Score breakdown:
        0–10 km    → ~5000 (near perfect)
        10–100 km  → 3000–5000 (great)
        100–500 km → 1000–3000 (good)
        500–2000   → 100–1000 (okay)
        2000+ km   → 0–100 (miss)

    Max score per round: 5000
    """
    if distance_km <= 0:
        return 5000

    # Exponential decay: score = 5000 * e^(-distance / 2000)
    score = 5000 * math.exp(-distance_km / 2000)
    return max(0, int(round(score)))


def build_streetview_url(lat: float, lng: float, api_key: str, size: str = "800x400") -> str:
    """
    Build a Google Street View Static API URL for a given location.

    Args:
        lat: Latitude
        lng: Longitude
        api_key: Google Maps API key
        size: Image dimensions (default 800x400)

    Returns:
        Full URL string for the Street View image
    """
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    return f"{base_url}?size={size}&location={lat},{lng}&fov=90&pitch=0&key={api_key}"
