import sqlite3

def show_stats():
    conn = sqlite3.connect('spotify_wrapped.db')
    cursor = conn.cursor()

    # 1. Total Count
    cursor.execute("SELECT COUNT(*) FROM streams")
    total = cursor.fetchone()[0]

    # 2. Top 5 Artists
    cursor.execute('''
        SELECT artist_name, COUNT(artist_name) as play_count 
        FROM streams 
        GROUP BY artist_name 
        ORDER BY play_count DESC 
        LIMIT 5
    ''')
    top_artists = cursor.fetchall()

    # 3. Top 5 Tracks
    cursor.execute('''
        SELECT track_name, artist_name, COUNT(track_name) as play_count 
        FROM streams 
        GROUP BY track_name, artist_name 
        ORDER BY play_count DESC 
        LIMIT 5
    ''')
    top_tracks = cursor.fetchall()

    # 4. Last 5 Tracks Added (Recent Activity)
    cursor.execute('''
        SELECT track_name, artist_name, played_at 
        FROM streams 
        ORDER BY played_at DESC 
        LIMIT 5
    ''')
    recent = cursor.fetchall()

    print("\n" + "="*40)
    print("      🎵 2025 SPOTIFY WRAPPED LIVE 🎵")
    print("="*40)
    print(f"📊 Total songs captured: {total}")
    
    print("\n🏆 TOP ARTISTS:")
    for i, (artist, count) in enumerate(top_artists, 1):
        print(f" {i}. {artist} ({count} plays)")

    print("\n🔥 TOP TRACKS:")
    for i, (track, artist, count) in enumerate(top_tracks, 1):
        print(f" {i}. {track} by {artist} ({count} plays)")

    print("\n🕙 RECENTLY SYNCED:")
    for track, artist, time in recent:
        print(f" • {track} - {artist}")
    print("="*40 + "\n")

    conn.close()

if __name__ == "__main__":
    show_stats()