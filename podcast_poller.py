import os
import sqlite3
import time
from datetime import datetime

from dotenv import load_dotenv

from spotify_auth import get_spotify_client as build_spotify_client

load_dotenv()


def save_podcast_stream(played_at, episode_name, show_name, publisher, ms_played, uri):
    conn = sqlite3.connect("podcasts.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcast_streams (
            played_at TEXT PRIMARY KEY,
            episode_name TEXT,
            show_name TEXT,
            publisher TEXT,
            ms_played INTEGER
        )
    ''')
    try:
        cursor.execute('''
            INSERT INTO podcast_streams VALUES (?, ?, ?, ?, ?)
        ''', (played_at, episode_name, show_name, publisher, ms_played))
        conn.commit()
        print(f"🎙️ Added Podcast Episode: {episode_name} ({show_name})")
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_spotify_client():
    return build_spotify_client(scope="user-read-currently-playing user-read-playback-state")


def iso_utc_now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def poll_current_playback():
    sp = get_spotify_client()
    last_saved_uri = None
    print("--- Podcast poller started. Listening for active episodes... 🎧")

    while True:
        try:
            result = sp.current_user_playing_track(additional_types=["episode"])
            if result and result.get("currently_playing_type") == "episode":
                episode = result.get("item")
                progress = result.get("progress_ms", 0)
                if episode is not None:
                    uri = episode.get("uri")
                    if uri and uri != last_saved_uri and progress >= 30000:
                        played_at = iso_utc_now()
                        episode_name = episode.get("name", "Unknown Episode")
                        show = episode.get("show", {})
                        show_name = show.get("name", "Unknown Podcast")
                        publisher = show.get("publisher", "Unknown Publisher")
                        ms_played = episode.get("duration_ms", 0)
                        if save_podcast_stream(played_at, episode_name, show_name, publisher, ms_played, uri):
                            last_saved_uri = uri
            else:
                last_saved_uri = None
        except Exception as error:
            print(f"❌ Poll error: {error}")

        time.sleep(20)


if __name__ == "__main__":
    poll_current_playback()
