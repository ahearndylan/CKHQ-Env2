import os
import json
import requests
from bs4 import BeautifulSoup
import time

IMG_DIR = "img"
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# Load players
with open("players.json", "r") as f:
    players = json.load(f)

# Scraper function
def fetch_image_from_nba_site(player_id, filename):
    url = f"https://www.nba.com/player/{player_id}"
    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"
        })
        soup = BeautifulSoup(response.text, "html.parser")

        img_tag = soup.find("img", attrs={"data-src": True})
        if img_tag:
            img_url = img_tag["data-src"]
        else:
            # fallback to regular <img src=...>
            img_tag = soup.find("img", attrs={"src": True})
            img_url = img_tag["src"] if img_tag else None

        if img_url and img_url.startswith("http"):
            ext = ".jpg" if ".jpg" in img_url else ".png"
            img_path = os.path.join(IMG_DIR, filename + ext)
            img_data = requests.get(img_url, timeout=10).content
            with open(img_path, "wb") as f:
                f.write(img_data)
            print(f"📥 Saved: {filename + ext}")
            return True
        else:
            print(f"❌ No image found for {filename}")
            return False
    except Exception as e:
        print(f"❌ Failed for {filename}: {e}")
        return False

# Run
for player in players:
    name = player.get("full_name")
    player_id = player.get("player_id")
    if not name or not player_id:
        continue

    filename = name.lower().replace(" ", "").replace("'", "")
    for ext in [".jpg", ".png"]:
        if os.path.exists(os.path.join(IMG_DIR, filename + ext)):
            print(f"✅ Already exists: {filename}{ext}")
            break
    else:
        fetch_image_from_nba_site(player_id, filename)
        time.sleep(2)  # gentle delay to avoid blocks

print("✅ Done downloading images.")
