import sqlite3

def show_stats():
    conn = sqlite3.connect('spotify_wrapped.db')
    cursor = conn.cursor()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM streams")
    total = cursor.fetchone()[0]

    # Get Top Artist
    cursor.execute('''
        SELECT artist_name, COUNT(artist_name) as play_count 
        FROM streams 
        GROUP BY artist_name 
        ORDER BY play_count DESC 
        LIMIT 5
    ''')
    top_artists = cursor.fetchall()

    print("--- 2025 WRAPPED PROGRESS ---")
    print(f"Total songs captured: {total}")
    print("\nTop 5 Artists so far:")
    for i, (artist, count) in enumerate(top_artists, 1):
        print(f"{i}. {artist} ({count} plays)")

    conn.close()

if __name__ == "__main__":
    show_stats()