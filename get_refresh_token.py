import os
from pathlib import Path

from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

ENV_FILE = Path(__file__).resolve().parent / ".env"


def save_refresh_token(token: str) -> None:
    if not ENV_FILE.exists():
        ENV_FILE.write_text(f"REFRESH_TOKEN={token}\n", encoding="utf-8")
        return

    lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    updated = False
    for index, line in enumerate(lines):
        if line.strip().startswith("REFRESH_TOKEN="):
            lines[index] = f"REFRESH_TOKEN={token}"
            updated = True
            break

    if not updated:
        lines.append(f"REFRESH_TOKEN={token}")

    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

# We initialize the manager just like your fetch script
auth_manager = SpotifyOAuth(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_uri=os.getenv("REDIRECT_URI"),
    scope="user-read-recently-played user-read-currently-playing user-read-playback-state"
)

# This checks if we have a token, and opens the browser if we need authorization.
cache_token = auth_manager.get_cached_token()
if cache_token is None:
    token_info = auth_manager.get_access_token(as_dict=False)
else:
    token_info = cache_token
print("--- Success! ---")
print("A hidden file named '.cache' has been created in this folder.")
if isinstance(token_info, dict):
    refresh_token = token_info.get("refresh_token")
else:
    refresh_token = auth_manager.cache_handler.get_cached_token().get("refresh_token") if auth_manager.cache_handler.get_cached_token() else None

if refresh_token:
    save_refresh_token(refresh_token)
    print("Refresh Token:", refresh_token)
    print(f"Saved to {ENV_FILE.name}")
else:
    print("Use the .cache file to retrieve your refresh token if it is not shown here.")