# 🎵 Personal Spotify Wrapped (24/7 Live)
### Track your music history every hour, forever. No more waiting for December.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Spotify-1DB954?style=for-the-badge&logo=spotify&logoColor=white" />
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
</p>

---

## 🧠 What is this?
Ever wondered who your **real** #1 artist is in the middle of July? This project is a "Personal Data Engineer" for your music. It uses a GitHub Robot to ask Spotify what you're listening to every hour and saves it into a permanent database.

> "Think of this like a little robot that sits in the cloud and writes down every song you play in a diary."

---

## 🛠️ The Tech Stack
- **Python**: The brain of the script.
- **Spotipy**: The bridge between our code and Spotify.
- **SQLite**: The "Vault" where all your songs are stored.
- **GitHub Actions**: The "Clockwork" that makes it run every hour for FREE.

---

## 🚀 Quick Setup (The 5-Minute Sprint)

### 1️⃣ Prepare your Environment
Make sure you have Python installed, then run this in your terminal:
```powershell
pip install spotipy python-dotenv

```

### 2️⃣ Get your Spotify Keys

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Create an App named **"My 24/7 Wrapped"**.
3. **CRITICAL:** Click `Edit Settings` and add `http://127.0.0.1:8888/callback` as your Redirect URI.
4. Copy your **Client ID** and **Client Secret**.

### 3️⃣ Generate your Magic Token

Run the setup script:

```powershell
python get_refresh_token.py

```

After your browser opens and you hit "Agree," run this magic line in your terminal to see your token:

```powershell
python -c "import json; print(json.load(open('.cache'))['refresh_token'])"

```

### 4️⃣ Set up your `.env` File

Create a file named `.env` and fill it like this:

```ini
CLIENT_ID=your_id_here
CLIENT_SECRET=your_secret_here
REDIRECT_URI=[http://127.0.0.1:8888/callback](http://127.0.0.1:8888/callback)
REFRESH_TOKEN=your_magic_token_here

```

---

## 🤖 Going Automatic (GitHub Cloud)

Don't want to keep your PC on? Let GitHub do it.

1. **Fork** this repo.
2. Go to `Settings > Secrets and variables > Actions`.
3. Add three secrets: `CLIENT_ID`, `CLIENT_SECRET`, and `REFRESH_TOKEN`.
4. Go to `Actions > General` and give **"Read and write permissions"** to workflows.
5. **Boom!** Your bot is now alive in the cloud.

---

## 📊 How to Flex your Stats

To see your rankings, just run:

```powershell
python check_stats.py

```

**It will show you:**

* ✅ Total songs captured
* 🏆 Top 5 Artists (Real-time)
* 🔥 Top 5 Tracks
* 🕙 Most recent syncs

---

## 🔧 Troubleshooting

| Error | Fix |
| --- | --- |
| `invalid_grant` | Your Refresh Token is old. Re-run Step 3. |
| `No module named 'spotipy'` | Run `pip install spotipy`. |
| `403 Forbidden` | Check your GitHub Actions permissions (Step 4). |

---

<p align="center">
Built with ❤️ for music lovers. 




<b>If this helped you, give it a ⭐ on GitHub!</b>
</p>

```

-----