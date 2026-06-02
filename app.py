import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
STREAM_DB = BASE_DIR / "spotify_wrapped.db"
PODCAST_DB = BASE_DIR / "podcasts.db"

app = FastAPI(title="Spotify Wrapped Dashboard API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def parse_iso_timestamp(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def build_time_window(range_name: str, year: Optional[int], month: Optional[int]):
    now = datetime.utcnow()
    if year and month:
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)
        return start, end
    if year:
        start = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)
        return start, end
    if range_name == "today":
        start = datetime(now.year, now.month, now.day)
        end = start + timedelta(days=1)
        return start, end
    if range_name == "7d":
        return now - timedelta(days=7), now
    if range_name == "30d":
        return now - timedelta(days=30), now
    return None, None


def filter_by_time(rows, range_name: str, year: Optional[int], month: Optional[int], played_at_index: int = 0):
    start, end = build_time_window(range_name, year, month)
    if not start:
        return rows
    filtered = []
    for row in rows:
        played_at = parse_iso_timestamp(row[played_at_index])
        if start <= played_at < end:
            filtered.append(row)
    return filtered


def group_metrics(rows):
    total_ms = 0
    track_counts = {}
    artist_counts = {}
    song_counts = {}
    unique_artists = set()
    unique_tracks = set()

    for played_at, track_name, artist_name, album_name, ms_played in rows:
        total_ms += ms_played or 0
        artist_counts[artist_name] = artist_counts.get(artist_name, 0) + 1
        song_key = f"{track_name} — {artist_name}"
        track_counts[song_key] = track_counts.get(song_key, 0) + 1
        unique_artists.add(artist_name)
        unique_tracks.add(track_name)

    top_artists = [
        {"artist": name, "plays": count}
        for name, count in sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    top_tracks = [
        {"track": name.split(" — ")[0], "artist": name.split(" — ")[1], "plays": count}
        for name, count in sorted(track_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    return {
        "total_listening_time_ms": total_ms,
        "total_tracks": len(rows),
        "unique_artists": len(unique_artists),
        "unique_tracks": len(unique_tracks),
        "top_artists": top_artists,
        "top_tracks": top_tracks,
    }


def load_genre_data(range_name: str, year: Optional[int], month: Optional[int]):
    conn = sqlite3.connect(STREAM_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT s.played_at, s.artist_name, g.genres FROM streams s LEFT JOIN artist_genres g ON s.artist_name = g.artist_name")
    rows = cursor.fetchall()
    conn.close()
    filtered = filter_by_time(rows, range_name, year, month)

    genre_counts = {}
    for played_at, artist_name, genres in filtered:
        if not genres:
            genres = "unknown"
        for raw in genres.split(","):
            name = raw.strip().lower()
            if not name:
                continue
            genre_counts[name] = genre_counts.get(name, 0) + 1

    return [
        {"genre": genre.title(), "plays": count}
        for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]


@app.get("/api/stats")
def stats(range: str = Query("all", pattern="^(all|30d|7d|today)$"), year: Optional[int] = None, month: Optional[int] = None):
    conn = sqlite3.connect(STREAM_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT played_at, track_name, artist_name, album_name, ms_played FROM streams")
    rows = cursor.fetchall()
    conn.close()

    filtered = filter_by_time(rows, range, year, month)
    metrics = group_metrics(filtered)
    metrics["top_genres"] = load_genre_data(range, year, month)
    metrics["range"] = range
    metrics["year"] = year
    metrics["month"] = month
    return metrics


@app.get("/api/habits")
def habits(range: str = Query("all", pattern="^(all|30d|7d|today)$"), year: Optional[int] = None, month: Optional[int] = None):
    conn = sqlite3.connect(STREAM_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT played_at FROM streams")
    rows = cursor.fetchall()
    conn.close()

    filtered = filter_by_time(rows, range, year, month, played_at_index=0)
    hours = {str(i).zfill(2): 0 for i in range(24)}
    weekday = {name: 0 for name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}

    for (played_at,) in filtered:
        dt = parse_iso_timestamp(played_at)
        hours[str(dt.hour).zfill(2)] += 1
        weekday[dt.strftime("%A")] += 1

    return {"hours": hours, "weekday": weekday}


@app.get("/api/podcasts")
def podcasts(range: str = Query("all", pattern="^(all|30d|7d|today)$"), year: Optional[int] = None, month: Optional[int] = None):
    conn = sqlite3.connect(PODCAST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT played_at, episode_name, show_name, publisher, ms_played FROM podcast_streams")
    rows = cursor.fetchall()
    conn.close()

    filtered = filter_by_time(rows, range, year, month, played_at_index=0)
    total_ms = sum((row[4] or 0) for row in filtered)
    show_counts = {}
    episode_counts = {}
    publisher_counts = {}

    for played_at, episode_name, show_name, publisher, ms_played in filtered:
        show_counts[show_name] = show_counts.get(show_name, 0) + 1
        episode_counts[f"{episode_name} — {show_name}"] = episode_counts.get(f"{episode_name} — {show_name}", 0) + 1
        publisher_counts[publisher] = publisher_counts.get(publisher, 0) + 1

    return {
        "total_podcast_hours": round(total_ms / 1000 / 60 / 60, 2),
        "episodes_listened": len(filtered),
        "unique_shows": len(show_counts),
        "top_shows": [{"show": name, "plays": count} for name, count in sorted(show_counts.items(), key=lambda x: x[1], reverse=True)[:5]],
        "top_episodes": [
            {"episode": item.split(" — ")[0], "show": item.split(" — ")[1], "plays": count}
            for item, count in sorted(episode_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ],
        "top_publishers": [{"publisher": name, "plays": count} for name, count in sorted(publisher_counts.items(), key=lambda x: x[1], reverse=True)[:5]],
    }


@app.get("/api/search")
def search(q: str = Query(..., min_length=1)):
    query = f"%{q.lower()}%"
    conn = sqlite3.connect(STREAM_DB)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT played_at, track_name, artist_name, album_name FROM streams WHERE lower(track_name) LIKE ? OR lower(artist_name) LIKE ? OR lower(album_name) LIKE ? ORDER BY played_at DESC LIMIT 50",
        (query, query, query),
    )
    music_rows = cursor.fetchall()
    conn.close()

    conn = sqlite3.connect(PODCAST_DB)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT played_at, episode_name, show_name, publisher FROM podcast_streams WHERE lower(episode_name) LIKE ? OR lower(show_name) LIKE ? OR lower(publisher) LIKE ? ORDER BY played_at DESC LIMIT 50",
        (query, query, query),
    )
    podcast_rows = cursor.fetchall()
    conn.close()

    return {
        "music": [
            {"played_at": row[0], "track": row[1], "artist": row[2], "album": row[3]}
            for row in music_rows
        ],
        "podcasts": [
            {"played_at": row[0], "episode": row[1], "show": row[2], "publisher": row[3]}
            for row in podcast_rows
        ],
    }


@app.get("/api/recent")
def recent():
    items = []
    conn = sqlite3.connect(STREAM_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT played_at, track_name, artist_name FROM streams ORDER BY played_at DESC LIMIT 10")
    for row in cursor.fetchall():
        items.append({"played_at": row[0], "type": "music", "title": row[1], "subtitle": row[2]})
    conn.close()

    conn = sqlite3.connect(PODCAST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT played_at, episode_name, show_name FROM podcast_streams ORDER BY played_at DESC LIMIT 10")
    for row in cursor.fetchall():
        items.append({"played_at": row[0], "type": "podcast", "title": row[1], "subtitle": row[2]})
    conn.close()

    sorted_items = sorted(items, key=lambda item: item["played_at"], reverse=True)[:10]
    return {"recent": sorted_items}


@app.get("/")
def homepage():
    return FileResponse(BASE_DIR / "static" / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000)
