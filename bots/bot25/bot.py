import os
import json
import requests
from duckduckgo_search import DDGS

IMG_DIR = "img"

# Load player list
with open("players.json", "r") as f:
    players = json.load(f)

# Create /img folder if it doesn't exist
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# Loop through players
for player in players:
    name = player["name"]
    filename = name.lower().replace(" ", "")
    
    # Skip if file already exists
    for ext in [".jpeg", ".jpg", ".png"]:
        if os.path.exists(os.path.join(IMG_DIR, filename + ext)):
            print(f"✅ Already exists: {filename + ext}")
            break
    else:
        query = f"{name} rookie basketball photo"
        print(f"🔍 Searching for: {query}")
        
        try:
            with DDGS() as ddgs:
                results = ddgs.images(query, max_results=1)
                if results:
                    image_url = results[0]["image"]
                else:
                    raise Exception("No image results found.")

            img_data = requests.get(image_url).content
            ext = ".jpg" if ".jpg" in image_url else ".png" if ".png" in image_url else ".jpeg"
            path = os.path.join(IMG_DIR, filename + ext)

            with open(path, "wb") as f:
                f.write(img_data)
            print(f"📥 Saved: {filename + ext}")

        except Exception as e:
            print(f"❌ Failed for {name}: {e}")
