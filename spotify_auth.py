import os
from pathlib import Path

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")


def clear_stored_spotify_auth():
    env_path = Path('.env')
    if env_path.exists():
        remaining_lines = [
            line for line in env_path.read_text(encoding='utf-8').splitlines()
            if not line.strip().startswith('REFRESH_TOKEN=')
        ]
        if remaining_lines:
            env_path.write_text("\n".join(remaining_lines) + "\n", encoding='utf-8')
        else:
            env_path.unlink()

    cache_path = Path('.cache')
    if cache_path.exists():
        cache_path.unlink()

    os.environ.pop('REFRESH_TOKEN', None)


def build_spotify_auth_manager(scope, client_id=None, client_secret=None, redirect_uri=None):
    return SpotifyOAuth(
        client_id=client_id or CLIENT_ID,
        client_secret=client_secret or CLIENT_SECRET,
        redirect_uri=redirect_uri or REDIRECT_URI,
        scope=scope,
    )


def get_spotify_client(scope, refresh_token=None):
    auth_manager = build_spotify_auth_manager(scope)
    try:
        token_info = auth_manager.refresh_access_token(refresh_token or os.getenv('REFRESH_TOKEN'))
    except Exception as exc:
        message = str(exc).lower()
        if 'invalid_grant' in message or 'expired' in message or 'authorization code' in message:
            clear_stored_spotify_auth()
            raise RuntimeError(
                'Spotify refresh token is no longer valid. Please re-authorize the app and update the refreshed token.'
            ) from exc
        raise
    return spotipy.Spotify(auth=token_info['access_token'])
