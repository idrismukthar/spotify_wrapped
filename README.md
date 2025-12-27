# 🎵 Personal Spotify Wrapped (24/7 Automation)

Stop waiting for December! This project automatically tracks every single song you listen to on Spotify and saves it into a permanent database using **GitHub Actions** and **Python**. Even if you close your laptop, the bot keeps working.

## 🚀 How it Works
1. **The Bot:** Every hour, a GitHub Action wakes up on a cloud server.
2. **The Fetch:** It talks to the Spotify API and asks "What did this person just listen to?"
3. **The Save:** New tracks are saved to `spotify_wrapped.db` and a log is updated in `last_run.txt`.
4. **The Flex:** You run a local script to see your real-time rankings.

---

## 🛠️ Setup Guide (For My Friends)

### 1. The Spotify Part
* Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
* Create an App called "My Wrapped".
* **Important:** Click 'Edit Settings' and add `http://127.0.0.1:8888/callback` as the **Redirect URI**.
* Copy your **Client ID** and **Client Secret**.

### 2. The GitHub Part
* **Fork** this repository to your own account.
* Go to your Fork's **Settings > Secrets and variables > Actions**.
* Add these 3 "New repository secrets":
  - `CLIENT_ID`: (Your Spotify ID)
  - `CLIENT_SECRET`: (Your Spotify Secret)
  - `REFRESH_TOKEN`: (The token you generate locally)
* Go to **Settings > Actions > General**, scroll to the bottom, and select **"Read and write permissions"**.

### 3. The Automation Part
* Go to the **Actions** tab in your repo.
* Select "Spotify Daily Sync" and click **Run workflow**.
* If it turns Green ✅, you are officially tracking!

---

## 📊 How to view your stats
To see your Top Artists and Tracks like I do in my videos:
1. `git pull origin main` (to get the latest data from the bot).
2. Run `python check_stats.py`.

---

## 👨‍💻 Tech Stack
- **Python**: Data processing.
- **SQLite**: Permanent database storage.
- **GitHub Actions**: Cloud automation (Cron Job).
- **Spotipy**: Spotify API library.