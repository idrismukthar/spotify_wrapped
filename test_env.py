import os
from dotenv import load_dotenv

load_dotenv()

print("Checking .env file...")
print(f"Client ID: {os.getenv('CLIENT_ID')}")
print(f"Client Secret: {os.getenv('CLIENT_SECRET')}")
print(f"Redirect URI: {os.getenv('REDIRECT_URI')}")
print("Environment variables loaded successfully.")
