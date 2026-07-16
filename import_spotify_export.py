import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path


def parse_spotify_timestamp(ts: str) -> str:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(ts, fmt)
            return dt.replace(microsecond=0).isoformat() + "Z"
        except Exception:
            continue
    return ts


def import_streaming_history(db_path: Path, export_paths: list):
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS streams (
            played_at TEXT PRIMARY KEY,
            track_name TEXT,
            artist_name TEXT,
            album_name TEXT,
            ms_played INTEGER
        )
    """)
    conn.commit()

    inserted = 0
    skipped = 0

    for p in export_paths:
        path = Path(p)
        if not path.exists():
            print(f"Skipping missing file: {path}")
            continue

        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            if "StreamingHistory" in data:
                rows = data["StreamingHistory"]
            else:
                rows = data.get("songs", [])
        else:
            rows = data

        for item in rows:
            end_time = item.get("ts") or item.get("endTime") or item.get("end_time") or item.get("timestamp")
            track_name = (
                item.get("master_metadata_track_name")
                or item.get("trackName")
                or item.get("track_name")
                or item.get("title")
            )
            artist_name = (
                item.get("master_metadata_album_artist_name")
                or item.get("artistName")
                or item.get("artist_name")
                or item.get("artist")
            )
            album_name = (
                item.get("master_metadata_album_album_name")
                or item.get("albumName")
                or item.get("album_name")
            )
            ms_played = item.get("ms_played") or item.get("msPlayed") or item.get("ms_played") or 0

            if not end_time or not track_name:
                skipped += 1
                continue

            played_at = parse_spotify_timestamp(str(end_time))
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO streams (played_at, track_name, artist_name, album_name, ms_played) VALUES (?, ?, ?, ?, ?)",
                    (played_at, track_name, artist_name, album_name, ms_played),
                )
                if cursor.rowcount:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as exc:
                print(f"DB insert error for {played_at}: {exc}")
                skipped += 1

    conn.commit()
    conn.close()
    print(f"Inserted: {inserted}, Skipped: {skipped}")


def main():
    parser = argparse.ArgumentParser(description="Import Spotify StreamingHistory JSON into spotify_wrapped.db")
    parser.add_argument("export_dir", help="Folder containing StreamingHistory JSON files")
    parser.add_argument("--db", default="spotify_wrapped.db", help="Path to sqlite DB")
    args = parser.parse_args()

    export_dir = Path(args.export_dir)
    if not export_dir.exists():
        print("Export folder not found:", export_dir)
        return

    files = sorted(export_dir.glob("*.json"))
    if not files:
        print("No JSON files found in", export_dir)
        return

    import_streaming_history(Path(args.db), [str(p) for p in files])


if __name__ == "__main__":
    main()
