import os
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from datetime import datetime

# Load variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

def save_podcast_stream(played_at, episode_name, show_name, publisher, ms_played):
    conn = sqlite3.connect('podcasts.db')
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
        # Already in DB
        return False
    finally:
        conn.close()

def save_music_stream_with_genres(played_at, track_name, artist_name, album_name, ms_played, sp):
    conn = sqlite3.connect('spotify_wrapped.db')
    cursor = conn.cursor()
    
    # 1. Insert into streams table
    try:
        cursor.execute('''
            INSERT INTO streams VALUES (?, ?, ?, ?, ?)
        ''', (played_at, track_name, artist_name, album_name, ms_played))
        print(f"✅ Added Track: {track_name} by {artist_name}")
        
        # 2. Check if artist genres already tracked
        cursor.execute("SELECT COUNT(*) FROM artist_genres WHERE artist_name = ?", (artist_name,))
        exists = cursor.fetchone()[0] > 0
        
        if not exists:
            # Query Spotify for the artist genres
            try:
                results = sp.search(q=f'artist:"{artist_name}"', type='artist', limit=1)
                items = results.get('artists', {}).get('items', [])
                if items:
                    artist_obj = items[0]
                    artist_id = artist_obj.get('id')
                    genres_list = artist_obj.get('genres', [])
                    genres_str = ", ".join(genres_list) if genres_list else "unknown"
                    cursor.execute("""
                        INSERT OR REPLACE INTO artist_genres (artist_name, artist_id, genres)
                        VALUES (?, ?, ?)
                    """, (artist_name, artist_id, genres_str))
                    print(f"   ✨ Auto-tracked Genres for '{artist_name}': {genres_str}")
                else:
                    cursor.execute("""
                        INSERT OR REPLACE INTO artist_genres (artist_name, artist_id, genres)
                        VALUES (?, ?, ?)
                    """, (artist_name, "not_found", "unknown"))
            except Exception as e:
                # Save as unknown on failure so we don't crash, we can retry later
                pass
                
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Track already in DB
        return False
    finally:
        conn.close()

def fetch_and_save():
    try:
        # Initialize databases and tables if not already exists
        conn_music = sqlite3.connect('spotify_wrapped.db')
        cursor_music = conn_music.cursor()
        cursor_music.execute('''
            CREATE TABLE IF NOT EXISTS streams (
                played_at TEXT PRIMARY KEY,
                track_name TEXT,
                artist_name TEXT,
                album_name TEXT,
                ms_played INTEGER
            )
        ''')
        cursor_music.execute('''
            CREATE TABLE IF NOT EXISTS artist_genres (
                artist_name TEXT PRIMARY KEY,
                artist_id TEXT,
                genres TEXT
            )
        ''')
        conn_music.commit()
        conn_music.close()

        auth_manager = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="user-read-recently-playing user-read-currently-playing user-read-playback-state"
        )
        token_info = auth_manager.refresh_access_token(REFRESH_TOKEN)
        sp = spotipy.Spotify(auth=token_info['access_token'])

        print("--- 🔍 Checking Spotify for new history ---")
        results = sp.current_user_recently_played(limit=50)
        
        added_tracks = 0
        added_podcasts = 0
        
        for item in results['items']:
            track = item.get('track')
            episode = item.get('episode')
            played_at = item.get('played_at')
            
            # If Spotify returns an episode under the 'track' key
            if track and track.get('type') == 'episode':
                episode = track
                track = None
                
            if episode:
                episode_name = episode.get('name', 'Unknown Episode')
                show = episode.get('show') or {}
                show_name = show.get('name', 'Unknown Podcast')
                publisher = show.get('publisher', 'Unknown Publisher')
                duration_ms = episode.get('duration_ms', 0)
                
                if save_podcast_stream(played_at, episode_name, show_name, publisher, duration_ms):
                    added_podcasts += 1
                    
            elif track:
                track_name = track.get('name', 'Unknown')
                artists = track.get('artists')
                artist_name = artists[0].get('name') if artists and len(artists) > 0 else 'Unknown Artist'
                album = track.get('album') or {}
                album_name = album.get('name', 'Unknown Album')
                duration_ms = track.get('duration_ms', 0)
                
                if save_music_stream_with_genres(played_at, track_name, artist_name, album_name, duration_ms, sp):
                    added_tracks += 1

        # Update the Verification Log
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("last_run.txt", "w") as f:
            f.write(f"Last successful sync: {now}\nNew tracks added: {added_tracks}\nNew podcasts added: {added_podcasts}")
            
        if added_tracks > 0 or added_podcasts > 0:
            print(f"\n✨ Success! Added {added_tracks} music tracks and {added_podcasts} podcasts.")
        else:
            print("\n☕ No new content found since last check.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_and_save()