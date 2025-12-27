import sqlite3

def create_db():
    # This creates the file 'spotify_wrapped.db' if it doesn't exist
    conn = sqlite3.connect('spotify_wrapped.db')
    cursor = conn.cursor()

    # Create the table
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

    conn.commit()
    conn.close()
    print("Database and table created successfully!")

if __name__ == "__main__":
    create_db()