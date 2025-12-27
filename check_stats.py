import sqlite3

conn = sqlite3.connect('spotify_wrapped.db')
cursor = conn.cursor()

# Query 1: Total count
cursor.execute("SELECT COUNT(*) FROM streams")
total = cursor.fetchone()[0]

# Query 2: Your current Top Artist based on these 50 songs
cursor.execute("SELECT artist_name, COUNT(*) as plays FROM streams GROUP BY artist_name ORDER BY plays DESC LIMIT 1")
top_artist = cursor.fetchone()

print(f"--- YOUR LOCAL WRAPPED PREVIEW ---")
print(f"Total songs captured so far: {total}")
print(f"Current #1 Artist: {top_artist[0]} ({top_artist[1]} plays)")

conn.close()