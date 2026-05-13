"""
GeoGuessr MVP — Streamlit Frontend
A polished geography guessing game with Street View images and interactive maps.
"""

import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import time

# ─── Config ──────────────────────────────────────────────────────────────────

API_BASE = "http://localhost:8000"
TOTAL_ROUNDS = 3
MAX_SCORE_PER_ROUND = 5000
MAX_TOTAL_SCORE = MAX_SCORE_PER_ROUND * TOTAL_ROUNDS

# Difficulty labels and emoji
DIFFICULTY_LABELS = {"easy": "🟢 Easy", "medium": "🟡 Medium", "hard": "🔴 Hard"}

# ─── Page Setup ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="GeoPinn ",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&family=Syne:wght@700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Dark game-like background */
    .stApp {
        background: linear-gradient(135deg, #0f1923 0%, #1a2a3a 50%, #0f1923 100%);
        color: #e8f4f8;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem !important; }

    /* ── Title ── */
    .game-title {
        font-family: 'Syne', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #00d4aa, #0099ff, #00d4aa);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s infinite linear;
        margin-bottom: 0;
        letter-spacing: -2px;
    }

    @keyframes shimmer {
        0% { background-position: 0% }
        100% { background-position: 200% }
    }

    .game-subtitle {
        text-align: center;
        color: #7ab8cc;
        font-size: 1.1rem;
        margin-top: 0.25rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        font-weight: 300;
    }

    /* ── Cards ── */
    .game-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(0,212,170,0.2);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        backdrop-filter: blur(10px);
        margin: 1rem 0;
    }

    /* ── Score display ── */
    .score-badge {
        display: inline-block;
        background: linear-gradient(135deg, #00d4aa22, #0099ff22);
        border: 1px solid #00d4aa66;
        border-radius: 50px;
        padding: 0.4rem 1.2rem;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        color: #00d4aa;
    }

    /* ── Round pill ── */
    .round-pill {
        display: inline-block;
        background: #0099ff22;
        border: 1px solid #0099ff66;
        border-radius: 50px;
        padding: 0.3rem 1rem;
        font-size: 0.9rem;
        color: #60c8ff;
        font-weight: 600;
    }

    /* ── Distance result ── */
    .result-distance {
        font-family: 'Syne', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        color: #00d4aa;
        text-align: center;
    }

    .result-label {
        color: #7ab8cc;
        text-align: center;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    /* ── Progress bar ── */
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 50px;
        height: 6px;
        margin: 0.5rem 0;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        border-radius: 50px;
        background: linear-gradient(90deg, #00d4aa, #0099ff);
        transition: width 0.5s ease;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #00d4aa, #0099ff) !important;
        color: #0f1923 !important;
        border: none !important;
        border-radius: 50px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.05em !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0,212,170,0.4) !important;
    }

    /* ── Street View image ── */
    .streetview-container img {
        border-radius: 12px;
        border: 2px solid rgba(0,212,170,0.3);
    }

    /* ── Leaderboard rows ── */
    .lb-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.07);
        font-size: 0.9rem;
    }

    .lb-rank {
        font-family: 'Syne', sans-serif;
        font-size: 1.2rem;
        font-weight: 800;
        color: #00d4aa;
        width: 2rem;
    }

    /* ── Metric cards ── */
    .metric-box {
        text-align: center;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(0,212,170,0.15);
        border-radius: 12px;
        padding: 1rem;
    }

    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #00d4aa;
    }

    .metric-label {
        font-size: 0.75rem;
        color: #7ab8cc;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    /* ── Info text ── */
    .hint-text {
        color: #7ab8cc;
        font-size: 0.85rem;
        text-align: center;
        font-style: italic;
    }

    /* ── Timer ── */
    .timer-display {
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #ff6b6b;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ─── Session State Initialization ────────────────────────────────────────────

def init_state():
    """Initialize or reset all session state variables."""
    defaults = {
        "screen": "start",          # start | playing | round_result | final | leaderboard
        "current_round": 1,
        "rounds_data": [],           # List of dicts: location + guess + result per round
        "current_location": None,   # Current location dict from API
        "guess_lat": None,
        "guess_lng": None,
        "round_result": None,        # API response after submitting a guess
        "total_score": 0,
        "difficulty": "all",
        "timer_start": None,
        "timer_seconds": 60,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def reset_game():
    """Reset game state to initial values for a new game."""
    keys_to_reset = [
        "current_round", "rounds_data", "current_location",
        "guess_lat", "guess_lng", "round_result", "total_score", "timer_start"
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["screen"] = "start"
    init_state()


# ─── API Helpers ─────────────────────────────────────────────────────────────

def fetch_random_location(difficulty: str = "all") -> dict | None:
    """Fetch a random location from the backend API."""
    try:
        resp = requests.get(
            f"{API_BASE}/game/random-location",
            params={"difficulty": difficulty},
            timeout=5
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"❌ Could not fetch location from API: {e}")
        return None


def submit_guess(round_number: int, guess_lat: float, guess_lng: float,
                 actual_lat: float, actual_lng: float) -> dict | None:
    """Submit a guess to the backend and receive distance/score."""
    try:
        payload = {
            "round_number": round_number,
            "guess_lat": guess_lat,
            "guess_lng": guess_lng,
            "actual_lat": actual_lat,
            "actual_lng": actual_lng,
        }
        resp = requests.post(
            f"{API_BASE}/game/submit-guess", json=payload, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"❌ Could not submit guess: {e}")
        return None


def fetch_leaderboard() -> list:
    """Fetch the top 10 leaderboard sessions."""
    try:
        resp = requests.get(f"{API_BASE}/game/leaderboard", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def get_streetview_url(lat: float, lng: float) -> str | None:
    """Get a Street View image URL from the backend."""
    try:
        resp = requests.get(
            f"{API_BASE}/game/streetview-url",
            params={"lat": lat, "lng": lng},
            timeout=5
        )
        if resp.status_code == 200:
            return resp.json().get("url")
    except Exception:
        pass
    return None


# ─── Map Helpers ─────────────────────────────────────────────────────────────

def make_guess_map(center_lat: float = 20.0, center_lng: float = 0.0) -> folium.Map:
    """Create an interactive world map for the player to click their guess."""
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=2,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )
    return m


def make_result_map(
    actual_lat: float, actual_lng: float,
    guess_lat: float, guess_lng: float
) -> folium.Map:
    """Create a result map showing actual location, guess, and connecting line."""
    mid_lat = (actual_lat + guess_lat) / 2
    mid_lng = (actual_lng + guess_lng) / 2

    m = folium.Map(
        location=[mid_lat, mid_lng],
        zoom_start=3,
        tiles="CartoDB dark_matter",
    )

    # Actual location marker (green)
    folium.Marker(
        location=[actual_lat, actual_lng],
        popup="📍 Actual Location",
        tooltip="Actual Location",
        icon=folium.Icon(color="green", icon="map-marker", prefix="fa"),
    ).add_to(m)

    # Guess marker (red)
    folium.Marker(
        location=[guess_lat, guess_lng],
        popup="🎯 Your Guess",
        tooltip="Your Guess",
        icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
    ).add_to(m)

    # Line connecting guess to actual
    folium.PolyLine(
        locations=[[actual_lat, actual_lng], [guess_lat, guess_lng]],
        color="#00d4aa",
        weight=2,
        dash_array="8 4",
        opacity=0.8,
    ).add_to(m)

    # Fit map to show both markers
    m.fit_bounds([[actual_lat, actual_lng], [
                 guess_lat, guess_lng]], padding=(40, 40))

    return m


# ─── Score Visual ─────────────────────────────────────────────────────────────

def score_color(score: int, max_score: int = 5000) -> str:
    ratio = score / max_score
    if ratio >= 0.8:
        return "#00d4aa"
    elif ratio >= 0.5:
        return "#0099ff"
    elif ratio >= 0.3:
        return "#ffaa00"
    else:
        return "#ff6b6b"


def render_score_bar(score: int, max_score: int = 5000):
    """Render an animated score progress bar."""
    pct = min(100, int(score / max_score * 100))
    color = score_color(score, max_score)
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-fill" style="width:{pct}%; background: linear-gradient(90deg, {color}, #0099ff);"></div>
    </div>
    """, unsafe_allow_html=True)


# ─── Screens ─────────────────────────────────────────────────────────────────

def screen_start():
    """Landing / start screen."""
    st.markdown('<div class="game-title">🌍 GeoPinn</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="game-subtitle">How well do you know the world?</div>',
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:

        st.markdown("### 🎮 How to Play")
        st.markdown("""
        1. **View** a Street View image from a mystery location
        2. **Click** on the world map to drop your guess
        3. **Score** points based on how close you are
        4. Play **3 rounds** — aim for the highest score!
        """)

        st.markdown("---")
        st.markdown("**⚙️ Difficulty**")
        difficulty = st.selectbox(
            "Select difficulty",
            options=["all", "easy", "medium", "hard"],
            format_func=lambda x: {"all": "🌐 Random Mix", "easy": "🟢 Easy (Famous Places)",
                                   "medium": "🟡 Medium (Cities)", "hard": "🔴 Hard (Remote)"}.get(x, x),
            label_visibility="collapsed",
        )
        st.session_state["difficulty"] = difficulty

        st.markdown('<br>', unsafe_allow_html=True)

        if st.button("▶  Start Game", use_container_width=True):
            with st.spinner("Loading first location…"):
                location = fetch_random_location(difficulty)
            if location:
                st.session_state["current_location"] = location
                st.session_state["screen"] = "playing"
                st.session_state["timer_start"] = time.time()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Leaderboard button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏆 View Leaderboard", use_container_width=True):
            st.session_state["screen"] = "leaderboard"
            st.rerun()


def screen_playing():
    """Main gameplay screen — show Street View and guess map."""
    location = st.session_state["current_location"]
    round_num = st.session_state["current_round"]
    total_score = st.session_state["total_score"]

    # ── Header Row ──
    h1, h2, h3 = st.columns([1, 2, 1])
    with h1:
        st.markdown(
            f'<div class="round-pill">Round {round_num} / {TOTAL_ROUNDS}</div>', unsafe_allow_html=True)
    with h2:
        st.markdown(
            '<div class="game-title" style="font-size:1.8rem;margin:0;">🌍 GeoGuessr</div>', unsafe_allow_html=True)
    with h3:
        st.markdown(
            f'<div style="text-align:right"><span class="score-badge">⭐ {total_score:,}</span></div>', unsafe_allow_html=True)

    # Progress dots
    dots = ""
    for i in range(1, TOTAL_ROUNDS + 1):
        color = "#00d4aa" if i < round_num else (
            "#0099ff" if i == round_num else "#334")
        dots += f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{color};margin:0 4px;"></span>'
    st.markdown(
        f'<div style="text-align:center;margin:0.5rem 0;">{dots}</div>', unsafe_allow_html=True)

    # ── Timer ──
    if st.session_state.get("timer_start"):
        elapsed = time.time() - st.session_state["timer_start"]
        remaining = max(0, int(st.session_state["timer_seconds"] - elapsed))
        timer_color = "#ff6b6b" if remaining < 15 else "#00d4aa"
        st.markdown(
            f'<div class="timer-display" style="color:{timer_color};">⏱ {remaining}s</div>', unsafe_allow_html=True)

    st.markdown("---")

    left_col, right_col = st.columns([1, 1], gap="medium")

    with left_col:
        st.markdown("#### 📸 Where in the world is this?")

        # ── Street View Image ──
        sv_url = get_streetview_url(location["lat"], location["lng"])
        if sv_url:
            st.image(sv_url, use_container_width=True,
                     caption="Street View — guess where this is!")
        else:
            # Fallback: show placeholder with coordinates hint removed
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.3);border:2px dashed rgba(0,212,170,0.3);
                        border-radius:12px;padding:3rem;text-align:center;color:#7ab8cc;">
                🗺️ Street View unavailable<br>
                <small>Add your Google Maps API key to .env to enable Street View images</small>
            </div>
            """, unsafe_allow_html=True)
            # Show a hint about the country in demo mode
            st.info(
                f"📍 Demo mode: Location is in **{location['country']}** ({DIFFICULTY_LABELS.get(location['difficulty'], location['difficulty'])})")

    with right_col:
        st.markdown("#### 🗺️ Click your guess on the map")
        st.markdown(
            '<p class="hint-text">Click anywhere to place your guess marker</p>', unsafe_allow_html=True)

        # ── Interactive Guess Map ──
        guess_map = make_guess_map()

        # If there's already a guess in state, show the marker
        if st.session_state["guess_lat"] and st.session_state["guess_lng"]:
            folium.Marker(
                location=[st.session_state["guess_lat"],
                          st.session_state["guess_lng"]],
                popup="Your Guess",
                icon=folium.Icon(color="blue", icon="crosshairs", prefix="fa"),
            ).add_to(guess_map)

        map_data = st_folium(
            guess_map,
            width="100%",
            height=380,
            key=f"guess_map_r{round_num}",
            returned_objects=["last_clicked"],
        )

        # Capture click
        if map_data and map_data.get("last_clicked"):
            clicked = map_data["last_clicked"]
            st.session_state["guess_lat"] = clicked["lat"]
            st.session_state["guess_lng"] = clicked["lng"]

        # Show current guess
        if st.session_state["guess_lat"]:
            st.markdown(f"""
            <div class="game-card" style="padding:0.8rem 1.2rem;margin-top:0.5rem;">
                🎯 Guess: <strong>{st.session_state['guess_lat']:.4f}°N, {st.session_state['guess_lng']:.4f}°E</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(
                '<p class="hint-text" style="margin-top:0.5rem;">No guess placed yet — click the map!</p>', unsafe_allow_html=True)

        # ── Submit Button ──
        if st.session_state["guess_lat"] is not None:
            if st.button("✅  Submit Guess", use_container_width=True):
                with st.spinner("Calculating distance…"):
                    result = submit_guess(
                        round_number=round_num,
                        guess_lat=st.session_state["guess_lat"],
                        guess_lng=st.session_state["guess_lng"],
                        actual_lat=location["lat"],
                        actual_lng=location["lng"],
                    )
                if result:
                    st.session_state["round_result"] = result
                    st.session_state["total_score"] += result["score"]
                    st.session_state["rounds_data"].append({
                        "round": round_num,
                        "location": location,
                        "guess_lat": st.session_state["guess_lat"],
                        "guess_lng": st.session_state["guess_lng"],
                        "distance_km": result["distance_km"],
                        "score": result["score"],
                    })
                    st.session_state["screen"] = "round_result"
                    st.rerun()
        else:
            st.button("✅  Submit Guess",
                      use_container_width=True, disabled=True)


def screen_round_result():
    """Show results after each round with map."""
    result = st.session_state["round_result"]
    round_num = st.session_state["current_round"]
    rd = st.session_state["rounds_data"][-1]  # Latest round data
    total_score = st.session_state["total_score"]

    # ── Header ──
    st.markdown(
        f'<div class="game-title" style="font-size:2rem;margin-bottom:0.5rem;">Round {round_num} Results</div>', unsafe_allow_html=True)

    # ── Metrics row ──
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{result['distance_km']:,.0f}</div>
            <div class="metric-label">km away</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value" style="color:{score_color(result['score'])};">{result['score']:,}</div>
            <div class="metric-label">points earned</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">⭐ {total_score:,}</div>
            <div class="metric-label">total score</div>
        </div>
        """, unsafe_allow_html=True)

    render_score_bar(result["score"])

    st.markdown("---")

    col_map, col_info = st.columns([2, 1])

    with col_map:
        st.markdown("#### 🗺️ Location Reveal")
        result_map = make_result_map(
            actual_lat=rd["location"]["lat"],
            actual_lng=rd["location"]["lng"],
            guess_lat=rd["guess_lat"],
            guess_lng=rd["guess_lng"],
        )
        st_folium(result_map, width="100%", height=420,
                  key=f"result_map_r{round_num}", returned_objects=[])

    with col_info:
        st.markdown("#### 📍 Location Info")
        st.markdown(f"""
        <div class="game-card">
            <div style="font-size:0.85rem;color:#7ab8cc;text-transform:uppercase;letter-spacing:0.1em;">Country</div>
            <div style="font-size:1.4rem;font-weight:700;margin-bottom:1rem;">{rd['location']['country']}</div>
            <div style="font-size:0.85rem;color:#7ab8cc;text-transform:uppercase;letter-spacing:0.1em;">Difficulty</div>
            <div style="margin-bottom:1rem;">{DIFFICULTY_LABELS.get(rd['location']['difficulty'], rd['location']['difficulty'])}</div>
            <div style="font-size:0.85rem;color:#7ab8cc;text-transform:uppercase;letter-spacing:0.1em;">Actual Coords</div>
            <div style="font-family:monospace;font-size:0.9rem;">{rd['location']['lat']:.4f}°, {rd['location']['lng']:.4f}°</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🎯 Your Guess")
        st.markdown(f"""
        <div class="game-card">
            <div style="font-family:monospace;font-size:0.9rem;">{rd['guess_lat']:.4f}°, {rd['guess_lng']:.4f}°</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Performance label ──
        dist = result["distance_km"]
        if dist < 50:
            perf = ("🎯 Incredible!", "#00d4aa")
        elif dist < 250:
            perf = ("🔥 Great shot!", "#0099ff")
        elif dist < 1000:
            perf = ("👍 Decent guess", "#ffaa00")
        elif dist < 3000:
            perf = ("😅 Not too bad", "#ff8844")
        else:
            perf = ("😬 Far off!", "#ff6b6b")

        st.markdown(
            f'<div style="text-align:center;font-size:1.3rem;font-weight:700;color:{perf[1]};margin:1rem 0;">{perf[0]}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Next / Finish Button ──
        is_last_round = round_num >= TOTAL_ROUNDS
        btn_label = "🏁  See Final Results" if is_last_round else f"➡️  Round {round_num + 1}"

        if st.button(btn_label, use_container_width=True):
            if is_last_round:
                st.session_state["screen"] = "final"
            else:
                # Load next location
                with st.spinner("Loading next location…"):
                    next_location = fetch_random_location(
                        st.session_state["difficulty"])
                if next_location:
                    st.session_state["current_location"] = next_location
                    st.session_state["current_round"] += 1
                    st.session_state["guess_lat"] = None
                    st.session_state["guess_lng"] = None
                    st.session_state["round_result"] = None
                    st.session_state["screen"] = "playing"
                    st.session_state["timer_start"] = time.time()
            st.rerun()


def screen_final():
    """Final results screen after all 3 rounds."""
    total_score = st.session_state["total_score"]
    rounds = st.session_state["rounds_data"]
    avg_distance = sum(r["distance_km"]
                       for r in rounds) / len(rounds) if rounds else 0

    # ── Title ──
    st.markdown('<div class="game-title">🏆 Game Over!</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="game-subtitle">Here\'s how you did</div>',
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Total score big display ──
    pct = total_score / MAX_TOTAL_SCORE
    if pct >= 0.8:
        rank, rank_color = "🌟 World Explorer", "#00d4aa"
    elif pct >= 0.6:
        rank, rank_color = "🗺️ Seasoned Traveler", "#0099ff"
    elif pct >= 0.4:
        rank, rank_color = "✈️ Globetrotter", "#ffaa00"
    elif pct >= 0.2:
        rank, rank_color = "🧭 Curious Wanderer", "#ff8844"
    else:
        rank, rank_color = "🏠 Stay-at-Home", "#ff6b6b"

    col_score, col_stats = st.columns([1, 1])

    with col_score:
        st.markdown(f"""
        <div class="game-card" style="text-align:center;padding:2rem;">
            <div style="color:#7ab8cc;font-size:0.9rem;text-transform:uppercase;letter-spacing:0.1em;">Final Score</div>
            <div style="font-family:'Syne',sans-serif;font-size:4rem;font-weight:800;color:#00d4aa;line-height:1;">
                {total_score:,}
            </div>
            <div style="color:#7ab8cc;font-size:0.85rem;">/ {MAX_TOTAL_SCORE:,} possible</div>
        </div>
        """, unsafe_allow_html=True)
        render_score_bar(total_score, MAX_TOTAL_SCORE)
        st.markdown(
            f'<div style="text-align:center;font-size:1.4rem;font-weight:700;color:{rank_color};margin-top:1rem;">{rank}</div>', unsafe_allow_html=True)

    with col_stats:
        st.markdown(f"""
        <div class="game-card">
            <div class="metric-box" style="margin-bottom:1rem;">
                <div class="metric-value">{avg_distance:,.0f} km</div>
                <div class="metric-label">Average Distance</div>
            </div>
        """, unsafe_allow_html=True)

        # Per-round breakdown
        st.markdown("**📊 Round Breakdown**")
        for rd in rounds:
            bar_pct = min(100, int(rd["score"] / MAX_SCORE_PER_ROUND * 100))
            c = score_color(rd["score"])
            st.markdown(f"""
            <div style="margin:0.4rem 0;">
                <div style="display:flex;justify-content:space-between;font-size:0.85rem;">
                    <span>Round {rd['round']} — {rd['location']['country']}</span>
                    <span style="color:{c};font-weight:700;">{rd['score']:,} pts</span>
                </div>
                <div style="font-size:0.75rem;color:#7ab8cc;margin-bottom:0.2rem;">{rd['distance_km']:,.0f} km away</div>
                <div class="progress-container">
                    <div class="progress-fill" style="width:{bar_pct}%;background:{c};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    btn1, btn2, btn3 = st.columns(3)
    with btn1:
        if st.button("🔄  Play Again", use_container_width=True):
            reset_game()
            st.rerun()
    with btn2:
        if st.button("🏆  Leaderboard", use_container_width=True):
            st.session_state["screen"] = "leaderboard"
            st.rerun()
    with btn3:
        if st.button("⚙️  Change Difficulty", use_container_width=True):
            reset_game()
            st.rerun()


def screen_leaderboard():
    """Display top 10 game sessions from SQLite."""
    st.markdown('<div class="game-title" style="font-size:2.5rem;">🏆 Leaderboard</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="game-subtitle">Top scoring games</div>',
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    sessions = fetch_leaderboard()

    col_lb, col_side = st.columns([2, 1])

    with col_lb:
        if not sessions:
            st.markdown("""
            <div class="game-card" style="text-align:center;padding:3rem;">
                <div style="font-size:3rem;">🎮</div>
                <div style="color:#7ab8cc;margin-top:1rem;">No games played yet.<br>Be the first on the leaderboard!</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            medals = ["🥇", "🥈", "🥉"]
            for i, session in enumerate(sessions):
                medal = medals[i] if i < 3 else f"#{i+1}"
                date_str = ""
                if session.get("played_at"):
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(
                            str(session["played_at"]).replace("Z", "+00:00"))
                        date_str = dt.strftime("%b %d, %Y")
                    except Exception:
                        date_str = "—"

                st.markdown(f"""
                <div class="game-card" style="padding:1rem 1.5rem;margin:0.5rem 0;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span style="font-size:1.5rem;">{medal}</span>
                            <span style="font-weight:700;margin-left:0.5rem;font-size:1.1rem;">{session['total_score']:,} pts</span>
                        </div>
                        <div style="color:#7ab8cc;font-size:0.85rem;">
                            📍 {session['avg_distance_km']} km avg &nbsp;|&nbsp; {date_str}
                        </div>
                    </div>
                    <div style="margin-top:0.5rem;display:flex;gap:1rem;">
                """, unsafe_allow_html=True)

                for rd in session.get("rounds", []):
                    c = score_color(rd["score"])
                    st.markdown(f"""
                    <span style="font-size:0.8rem;background:rgba(255,255,255,0.05);
                                border-radius:6px;padding:0.2rem 0.5rem;color:{c};">
                        R{rd['round']}: {rd['score']:,}
                    </span>
                    """, unsafe_allow_html=True)

                st.markdown("</div></div>", unsafe_allow_html=True)

    with col_side:
        st.markdown("""
        <div class="game-card" style="text-align:center;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">📊</div>
            <div style="color:#7ab8cc;font-size:0.85rem;">Score guide</div>
            <div style="margin-top:1rem;font-size:0.85rem;text-align:left;">
                <div style="color:#00d4aa;margin:0.3rem 0;">🌟 4,000–5,000 · &lt;10 km</div>
                <div style="color:#0099ff;margin:0.3rem 0;">🔥 3,000–4,000 · &lt;100 km</div>
                <div style="color:#ffaa00;margin:0.3rem 0;">👍 2,000–3,000 · &lt;300 km</div>
                <div style="color:#ff8844;margin:0.3rem 0;">😅 1,000–2,000 · &lt;1000 km</div>
                <div style="color:#ff6b6b;margin:0.3rem 0;">😬 0–1,000 · 1000+ km</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔄  Refresh", use_container_width=True):
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Menu", use_container_width=False):
        st.session_state["screen"] = "start"
        st.rerun()


# ─── Main Router ─────────────────────────────────────────────────────────────

def main():
    init_state()

    screen = st.session_state["screen"]

    if screen == "start":
        screen_start()
    elif screen == "playing":
        screen_playing()
    elif screen == "round_result":
        screen_round_result()
    elif screen == "final":
        screen_final()
    elif screen == "leaderboard":
        screen_leaderboard()
    else:
        st.error(f"Unknown screen: {screen}")
        reset_game()


if __name__ == "__main__":
    main()
