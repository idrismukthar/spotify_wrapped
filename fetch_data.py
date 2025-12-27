import os
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# 1. Load Environment Variables (Works for local .env and GitHub Secrets)
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

def get_spotify_client():
    """Authenticates using the Refresh Token (No browser needed)"""
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-read-recently-played"
    )
    
    # Refresh the access token using our Golden Key
    token_info = auth_manager.refresh_access_token(REFRESH_TOKEN)
    return spotipy.Spotify(auth=token_info['access_token'])

def fetch_and_save():
    # Connect to your database
    conn = sqlite3.connect('spotify_wrapped.db')
    cursor = conn.cursor()

    print("Checking Spotify for new tracks...")
    
    try:
        sp = get_spotify_client()
        results = sp.current_user_recently_played(limit=50)
        
        count = 0
        for item in results['items']:
            track = item['track']
            played_at = item['played_at']
            name = track['name']
            artist = track['artists'][0]['name']
            album = track['album']['name']
            duration = track['duration_ms']

            try:
                cursor.execute('''
                    INSERT INTO streams (played_at, track_name, artist_name, album_name, ms_played)
                    VALUES (?, ?, ?, ?, ?)
                ''', (played_at, name, artist, album, duration))
                count += 1
                print(f"New track added: {name} by {artist}")
            except sqlite3.IntegrityError:
                # Already in database
                continue

        conn.commit()
        print(f"Finished! Added {count} new tracks.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_and_save()