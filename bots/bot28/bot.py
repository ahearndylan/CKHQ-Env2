import json
import os
from datetime import datetime
import requests
import tweepy
import tempfile

# ======================= #
# TWITTER AUTHENTICATION  #
# ======================= #
bearer_token = "AAAAAAAAAAAAAAAAAAAAAPztzwEAAAAAvBGCjApPNyqj9c%2BG7740SkkTShs%3DTCpOQ0DMncSMhaW0OA4UTPZrPRx3BHjIxFPzRyeoyMs2KHk6hM"
api_key = "uKyGoDr5LQbLvu9i7pgFrAnBr"
api_secret = "KGBVtj1BUmAEsyoTmZhz67953ItQ8TIDcChSpodXV8uGMPXsoH"
access_token = "1901441558596988929-WMdEPOtNDj7QTJgLHVylxnylI9ObgD"
access_token_secret = "9sf83R8A0MBdijPdns6nWaG7HF47htcWo6oONPmMS7o98"

client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api_v1 = tweepy.API(auth)

# ======================= #
# LOAD PLAYER DATA        #
# ======================= #
base_dir = os.path.dirname(os.path.abspath(__file__))
players_file = os.path.join(base_dir, "players.json")

with open(players_file, "r") as f:
    players = json.load(f)

# ======================= #
# CHECK FOR BIRTHDAYS     #
# ======================= #
today = datetime.today().strftime("%m-%d")
birthdays_today = [p for p in players if p["birthdate"][5:] == today]

if not birthdays_today:
    print("🎂 No birthdays today for notable players.")
    exit()

# ======================= #
# HEADSHOT HELPER         #
# ======================= #
def fetch_headshot_image(player_id):
    url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            with open(temp_file.name, "wb") as f:
                f.write(response.content)
            return temp_file.name
    except Exception as e:
        print(f"❌ Error downloading image for player_id {player_id}: {e}")
    return None

# ======================= #
# POST TWEETS             #
# ======================= #
for player in birthdays_today:
    name = player["full_name"]
    birth_year = player["birthdate"][:4]
    age = datetime.today().year - int(birth_year)

    tweet_text = f"""🎉 Happy Birthday to NBA player {name}!

Born on this day in {birth_year}, {name} turns {age} today 🥳

Wishing a big year ahead! 🎂

#NBABirthday #CourtKingsHQ
"""

    media_id = None
    if player.get("player_id"):
        img_path = fetch_headshot_image(player["player_id"])
        if img_path:
            try:
                uploaded = api_v1.media_upload(img_path)
                media_id = uploaded.media_id
                os.remove(img_path)  # Clean up
            except Exception as e:
                print(f"❌ Error uploading image for {name}: {e}")

    try:
        if media_id:
            client.create_tweet(text=tweet_text, media_ids=[media_id])
        else:
            client.create_tweet(text=tweet_text)
        print(f"✅ Tweet posted for {name}")
    except Exception as e:
        print(f"❌ Error posting tweet for {name}: {e}")
