import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

# We initialize the manager just like your fetch script
auth_manager = SpotifyOAuth(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_uri=os.getenv("REDIRECT_URI"),
    scope="user-read-recently-played"
)

# This checks if we have a token, if not, it opens the browser
token_info = auth_manager.get_access_token(as_dict=False)
print("--- Success! ---")
print("A hidden file named '.cache' has been created in this folder.")
print("Open it to find your Refresh Token.")