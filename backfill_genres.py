import os
import sqlite3
import time

from dotenv import load_dotenv

from spotify_auth import get_spotify_client

# Load variables
load_dotenv()

def backfill():
    print("--- Starting Genres Backfill Process ---")
    
    # 1. Connect to database
    conn = sqlite3.connect('spotify_wrapped.db')
    cursor = conn.cursor()
    
    # 2. Get all unique artist names
    cursor.execute("SELECT DISTINCT artist_name FROM streams")
    all_artists = [row[0] for row in cursor.fetchall() if row[0]]
    print(f"Total unique artists in history: {len(all_artists)}")
    
    # 3. Get already backfilled artists
    cursor.execute("SELECT artist_name FROM artist_genres")
    existing_artists = set(row[0] for row in cursor.fetchall())
    print(f"Already backfilled artists: {len(existing_artists)}")
    
    # Artists to backfill
    to_backfill = [a for a in all_artists if a not in existing_artists]
    print(f"Artists remaining to backfill: {len(to_backfill)}")
    
    if not to_backfill:
        print("All artists are already backfilled! Nothing to do.")
        conn.close()
        return

    # 4. Setup Spotify
    sp = get_spotify_client(scope="user-read-recently-played")
    
    count = 0
    errors = 0
    
    for i, artist_name in enumerate(to_backfill, 1):
        # Prevent terminal encoding crashes on Windows by cleaning the artist name for printing
        safe_print_name = artist_name.encode('ascii', 'ignore').decode('ascii')
        print(f"[{i}/{len(to_backfill)}] Searching for artist: '{safe_print_name}' ...", end="", flush=True)
        
        try:
            # Search Spotify for this artist by name
            # Using double quotes around artist name for an exact match search
            results = sp.search(q=f'artist:"{artist_name}"', type='artist', limit=1)
            items = results.get('artists', {}).get('items', [])
            
            if items:
                artist_obj = items[0]
                artist_id = artist_obj.get('id')
                genres_list = artist_obj.get('genres', [])
                genres_str = ", ".join(genres_list) if genres_list else "unknown"
                
                # Insert/Update in the database
                cursor.execute("""
                    INSERT OR REPLACE INTO artist_genres (artist_name, artist_id, genres)
                    VALUES (?, ?, ?)
                """, (artist_name, artist_id, genres_str))
                
                # Commit every 20 records to save progress
                if count % 20 == 0:
                    conn.commit()
                    
                print(f" Found! Genres: {genres_str}")
                count += 1
            else:
                # Artist not found on Spotify
                cursor.execute("""
                    INSERT OR REPLACE INTO artist_genres (artist_name, artist_id, genres)
                    VALUES (?, ?, ?)
                """, (artist_name, "not_found", "unknown"))
                print(" Not found on Spotify (marked as unknown).")
                
            # Respectful rate limiting
            time.sleep(0.15)
            
        except Exception as e:
            print(f" Error occurred: {e}")
            errors += 1
            # If we hit an issue (e.g. rate limit), wait longer
            time.sleep(2)
            
    conn.commit()
    conn.close()
    
    print("\n--- Backfill Process Finished ---")
    print(f"Successfully backfilled: {count} artists.")
    if errors > 0:
        print(f"Encountered errors: {errors} artists.")

if __name__ == "__main__":
    backfill()
