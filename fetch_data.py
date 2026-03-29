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

def fetch_and_save():
    conn = sqlite3.connect('spotify_wrapped.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streams (
            played_at TEXT PRIMARY KEY,
            track_name TEXT,
            artist_name TEXT,
            album_name TEXT,
            ms_played INTEGER
        )
    ''')

    try:
        auth_manager = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI
        )
        token_info = auth_manager.refresh_access_token(REFRESH_TOKEN)
        sp = spotipy.Spotify(auth=token_info['access_token'])

        print("--- 🔍 Checking Spotify for new tracks ---")
        results = sp.current_user_recently_played(limit=50)
        
        count = 0
        for item in results['items']:
            track = item.get('track') or {}
            played_at = item.get('played_at')
            track_name = track.get('name', 'Unknown')
            
            # Check if it's a track or a podcast episode
            if track.get('type') == 'episode':
                show = track.get('show') or {}
                artist_name = show.get('name', 'Unknown Podcast')
                album_name = show.get('publisher', 'Podcast')
            else:
                artists = track.get('artists')
                artist_name = artists[0].get('name') if artists and len(artists) > 0 else 'Unknown Artist'
                album = track.get('album') or {}
                album_name = album.get('name', 'Unknown Album')

            try:
                cursor.execute('''
                    INSERT INTO streams VALUES (?, ?, ?, ?, ?)
                ''', (played_at, track_name, artist_name, album_name, track.get('duration_ms', 0)))
                
                # THIS IS THE NEW PART:
                print(f"✅ Added: {track_name} by {artist_name}")
                count += 1
            except sqlite3.IntegrityError:
                # This song is already in the DB, so we skip it
                continue

        conn.commit()
        
        # Update the Verification Log
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("last_run.txt", "w") as f:
            f.write(f"Last successful sync: {now}\nNew tracks added: {count}")
            
        if count > 0:
            print(f"\n✨ Success! Total new tracks added: {count}")
        else:
            print("\n☕ No new tracks found since last check.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_and_save()