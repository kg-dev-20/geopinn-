

from .database import SessionLocal, engine, Base
from .models import Location

# 25 diverse locations across all continents
SEED_LOCATIONS = [
    # ── Easy (famous landmarks / tourist areas) ──────────────────────────────
    {"lat": 48.8584, "lng": 2.2945,    "country": "France",
        "difficulty": "easy"},   # Eiffel Tower
    {"lat": 40.6892, "lng": -74.0445,  "country": "USA",
        "difficulty": "easy"},   # Statue of Liberty
    {"lat": -22.9519, "lng": -43.2105,  "country": "Brazil",
        "difficulty": "easy"},   # Rio de Janeiro
    {"lat": 27.1751, "lng": 78.0421,   "country": "India",
        "difficulty": "easy"},   # Taj Mahal
    {"lat": -33.8568, "lng": 151.2153,  "country": "Australia",
        "difficulty": "easy"},   # Sydney Opera House
    {"lat": 51.5081, "lng": -0.0759,   "country": "UK",
        "difficulty": "easy"},   # Tower Bridge

    # ── Medium (cities, scenic routes) ───────────────────────────────────────
    {"lat": 35.6762, "lng": 139.6503,  "country": "Japan",
        "difficulty": "medium"},  # Tokyo
    {"lat": 55.7558, "lng": 37.6173,   "country": "Russia",
        "difficulty": "medium"},  # Moscow
    {"lat": -1.2921, "lng": 36.8219,   "country": "Kenya",
        "difficulty": "medium"},  # Nairobi
    {"lat": 30.0444, "lng": 31.2357,   "country": "Egypt",
        "difficulty": "medium"},  # Cairo
    {"lat": 19.4326, "lng": -99.1332,  "country": "Mexico",
        "difficulty": "medium"},  # Mexico City
    {"lat": 41.0082, "lng": 28.9784,   "country": "Turkey",
        "difficulty": "medium"},  # Istanbul
    {"lat": -26.2041, "lng": 28.0473,   "country": "South Africa",
        "difficulty": "medium"},  # Johannesburg
    {"lat": 1.3521,  "lng": 103.8198,  "country": "Singapore",
        "difficulty": "medium"},  # Singapore
    {"lat": 59.9139, "lng": 10.7522,   "country": "Norway",
        "difficulty": "medium"},  # Oslo
    {"lat": 25.2048, "lng": 55.2708,   "country": "UAE",
        "difficulty": "medium"},  # Dubai

    # ── Hard (remote / rural / unusual locations) ─────────────────────────────
    {"lat": -54.8019, "lng": -68.3030,  "country": "Argentina",
        "difficulty": "hard"},   # Ushuaia (Patagonia)
    {"lat": 64.1265, "lng": -21.8174,  "country": "Iceland",
        "difficulty": "hard"},   # Reykjavik outskirts
    {"lat": -8.3405, "lng": 115.0920,  "country": "Indonesia",
        "difficulty": "hard"},   # Bali countryside
    {"lat": 27.7172, "lng": 85.3240,   "country": "Nepal",
        "difficulty": "hard"},   # Kathmandu valley
    {"lat": 9.0579,  "lng": 7.4951,    "country": "Nigeria",
        "difficulty": "hard"},   # Abuja
    {"lat": 60.1699, "lng": 24.9384,   "country": "Finland",
        "difficulty": "hard"},   # Helsinki outskirts
    {"lat": -15.7975, "lng": -47.8919,  "country": "Brazil",
        "difficulty": "hard"},   # Brasília
    {"lat": 43.2965, "lng": 5.3698,    "country": "France",
        "difficulty": "hard"},   # Marseille port
    {"lat": 39.9042, "lng": 116.4074,  "country": "China",
        "difficulty": "hard"},   # Beijing suburbs
]


def seed_database():
    """
    Create all tables and insert seed locations if not already present.
    Safe to call multiple times — skips seeding if data exists.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(Location).count()
        if existing > 0:
            print(
                f"[seed] Database already has {existing} locations. Skipping seed.")
            return

        locations = [Location(**loc) for loc in SEED_LOCATIONS]
        db.add_all(locations)
        db.commit()
        print(f"[seed] Successfully seeded {len(locations)} locations.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
