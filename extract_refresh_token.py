#!/usr/bin/env python3
"""extract_refresh_token.py

Find a Spotipy `.cache` file in the current folder, extract the refresh_token,
print it, and optionally write it into `.env` as REFRESH_TOKEN.

Usage:
  python extract_refresh_token.py         # just prints token(s)
  python extract_refresh_token.py --update  # write first found token to .env
"""

import json
import glob
import os
import re
import argparse


def find_cache_files():
    # Look for common cache filenames: .cache and .cache-* patterns
    files = [".cache"] + glob.glob(".cache*")
    # Remove directories and duplicates
    files = [f for f in dict.fromkeys(files) if os.path.isfile(f)]
    return files


def extract_from_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
            try:
                data = json.loads(text)
                # token may be top-level or nested
                if isinstance(data, dict):
                    # try known keys
                    for key in ("refresh_token", "refreshToken", "refresh"):
                        if key in data:
                            return data[key]
                    # explore nested dicts
                    for v in data.values():
                        if isinstance(v, dict) and "refresh_token" in v:
                            return v["refresh_token"]
            except Exception:
                # Not valid JSON, fall through to regex
                pass
            m = re.search(r'"refresh_token"\s*:\s*"([^"]+)"', text)
            if m:
                return m.group(1)
    except Exception:
        pass
    return None


def update_env_token(token):
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith("REFRESH_TOKEN="):
                lines[i] = f"REFRESH_TOKEN={token}\n"
                found = True
                break
        if not found:
            lines.append(f"REFRESH_TOKEN={token}\n")
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
    else:
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"REFRESH_TOKEN={token}\n")


def main():
    parser = argparse.ArgumentParser(description="Extract refresh_token from Spotipy cache (.cache) files.")
    parser.add_argument("--update", "-u", action="store_true", help="Write the found token to .env as REFRESH_TOKEN")
    args = parser.parse_args()

    files = find_cache_files()
    if not files:
        print("No .cache files found in the current directory. Try running python get_refresh_token.py first.")
        return

    tokens = []
    for f in files:
        t = extract_from_file(f)
        if t:
            tokens.append((f, t))

    if not tokens:
        print("No refresh_token found inside detected .cache files. Open the cache file and check its contents.")
        return

    print("Found refresh token(s):")
    for i, (f, t) in enumerate(tokens, 1):
        display = t if len(t) < 60 else t[:28] + "..." + t[-28:]
        print(f" {i}. {f}: {display}")

    # Use the first token by default
    token = tokens[0][1]

    if args.update:
        update_env_token(token)
        print("REFRESH_TOKEN written to .env (or updated).")
    else:
        print("\nFull token:\n")
        print(token)


if __name__ == "__main__":
    main()
