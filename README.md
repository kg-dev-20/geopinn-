# 🌍 GeoGuessr MVP

A full-stack GeoGuessr-style geography guessing game built with **FastAPI**, **Streamlit**, **SQLite**, and **Google Street View**.

---

## 📁 Project Structure

```
geoguessr-mvp/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   ├── models.py        # ORM models (Location, GameResult)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── seed.py          # Database seeder (25 world locations)
│   │   ├── routes/
│   │   │   └── game.py      # API endpoints
│   │   └── services/
│   │       └── geo.py       # Haversine + scoring logic
│   │
│   ├── requirements.txt
│   └── .env                 # Google Maps API key
│
├── frontend/
│   ├── app.py               # Streamlit UI (all screens)
│   └── requirements.txt
│
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- A Google Maps API key with **Street View Static API** enabled
  - Get one at: https://console.cloud.google.com/
  - Enable: `Maps Static API` and `Street View Static API`

---

### 1. Clone / Download

```bash
cd geoguessr-mvp
```

---

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your API key
# Edit .env and replace the placeholder:
# GOOGLE_MAPS_API_KEY=your_actual_key_here
nano .env
```

#### Initialize & Seed Database

The database is automatically created and seeded on first startup. To manually seed:

```bash
python -m app.seed
```

This creates `geoguessr.db` in the `backend/` directory with 25 world locations.

#### Start FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

---

### 3. Frontend Setup

```bash
# Open a new terminal
cd frontend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Streamlit
streamlit run app.py --server.port 8501
```

Open your browser at: **http://localhost:8501**

---

## 🎮 Gameplay

1. **Start Screen** — Choose difficulty (Easy / Medium / Hard / Random Mix)
2. **Round Screen** — View a Street View image, click the world map to guess
3. **Result Screen** — See your distance, score, and a map showing both markers
4. **Final Screen** — View total score, rank, and per-round breakdown
5. **Leaderboard** — Top 10 games stored in SQLite

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/game/random-location` | Get a random game location |
| `GET` | `/game/streetview-url` | Generate Street View image URL |
| `POST` | `/game/submit-guess` | Submit a guess, get distance + score |
| `GET` | `/game/results` | All stored game results |
| `GET` | `/game/leaderboard` | Top 10 game sessions |

### Example Requests

```bash
# Get a random location
curl http://localhost:8000/game/random-location

# Get a hard location
curl "http://localhost:8000/game/random-location?difficulty=hard"

# Submit a guess
curl -X POST http://localhost:8000/game/submit-guess \
  -H "Content-Type: application/json" \
  -d '{
    "round_number": 1,
    "guess_lat": 48.85,
    "guess_lng": 2.35,
    "actual_lat": 48.8584,
    "actual_lng": 2.2945
  }'
```

---

## 🏆 Scoring System

Uses exponential decay based on distance:

```
score = 5000 × e^(−distance_km / 2000)
```

| Distance | Score |
|----------|-------|
| 0–10 km | ~4,975 – 5,000 |
| 10–100 km | ~3,000 – 4,975 |
| 100–500 km | ~1,287 – 3,000 |
| 500–2000 km | ~184 – 1,287 |
| 2000+ km | 0 – 184 |

Max per round: **5,000** · Max total: **15,000**

---

## 🗄️ Database Schema

### `locations`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| lat | FLOAT | Latitude |
| lng | FLOAT | Longitude |
| country | VARCHAR | Country name |
| difficulty | VARCHAR | easy / medium / hard |

### `game_results`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| round_number | INTEGER | 1, 2, or 3 |
| guess_lat | FLOAT | Player's guessed latitude |
| guess_lng | FLOAT | Player's guessed longitude |
| actual_lat | FLOAT | True latitude |
| actual_lng | FLOAT | True longitude |
| distance | FLOAT | Distance in km (Haversine) |
| score | INTEGER | Points earned |
| created_at | DATETIME | Timestamp |

---

## ⚙️ Environment Variables

Create `backend/.env`:

```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

> **Note**: Without an API key, the app runs in "demo mode" — gameplay still works but Street View images won't display. The country name is shown as a hint instead.

---

## 🛠️ Troubleshooting

**Backend won't start**
- Ensure you're in the `backend/` directory when running uvicorn
- Check Python version: `python --version` (needs 3.10+)

**Frontend can't connect to API**
- Make sure the backend is running on port 8000
- Check CORS settings in `backend/app/main.py`

**No Street View image**
- Verify your API key in `.env`
- Ensure Street View Static API is enabled in Google Cloud Console
- Some remote locations may not have Street View coverage

**Database issues**
- Delete `backend/geoguessr.db` and restart — it will be recreated and reseeded

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit + streamlit-folium + Folium |
| Backend | FastAPI + Uvicorn |
| Database | SQLite via SQLAlchemy ORM |
| Maps | Folium (CartoDB Dark Matter tiles) |
| Street View | Google Maps Street View Static API |
| Distance | Haversine formula |

---

## 📝 License

MIT — build and extend freely!
