import sqlite3

def create_db():
    # This creates the file 'spotify_wrapped.db' if it doesn't exist
    conn = sqlite3.connect('spotify_wrapped.db')
    cursor = conn.cursor()

    # Create the streams table
    # 'played_at' is the PRIMARY KEY because Spotify gives a unique timestamp 
    # for every play. This prevents us from saving the same play twice.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streams (
            played_at TEXT PRIMARY KEY,
            track_name TEXT,
            artist_name TEXT,
            album_name TEXT,
            ms_played INTEGER
        )
    ''')

    # Create the artist_genres table to associate artists with their genres
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artist_genres (
            artist_name TEXT PRIMARY KEY,
            artist_id TEXT,
            genres TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("Music database and tables created successfully!")

    # Create the podcasts database and table
    conn_podcasts = sqlite3.connect('podcasts.db')
    cursor_podcasts = conn_podcasts.cursor()
    cursor_podcasts.execute('''
        CREATE TABLE IF NOT EXISTS podcast_streams (
            played_at TEXT PRIMARY KEY,
            episode_name TEXT,
            show_name TEXT,
            publisher TEXT,
            ms_played INTEGER
        )
    ''')
    conn_podcasts.commit()
    conn_podcasts.close()
    print("Podcast database and table created successfully!")

if __name__ == "__main__":
    create_db()