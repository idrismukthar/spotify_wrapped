import time
import os
import sqlite3
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load keys
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Setup Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-read-recently-played",
    open_browser=False # Stops it from opening a browser every time it runs
))

def fetch_and_save():
    try:
        conn = sqlite3.connect('spotify_wrapped.db')
        cursor = conn.cursor()
        results = sp.current_user_recently_played(limit=50)
        
        for item in results['items']:
            track = item.get('track') or {}
            played_at = item.get('played_at')
            
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
                ''', (played_at, track.get('name', 'Unknown'), artist_name, album_name, track.get('duration_ms', 0)))
            except sqlite3.IntegrityError:
                continue
        conn.commit()
        conn.close()
    except Exception as e:
        # If internet is down or API is busy, just wait for the next loop
        pass

# The "Always On" Loop
while True:
    fetch_and_save()
    # Sleep for 45 minutes (2700 seconds)
    # This ensures we catch everything (since 50 songs is usually > 45 mins)
    time.sleep(2700)