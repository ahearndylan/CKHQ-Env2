import os
import json
from datetime import date, datetime
import tweepy
import random

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
# CONFIG & PATHS          #
# ======================= #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIRTHDAYS_JSON = os.path.join(BASE_DIR, "players_birthdays.json")
HEADSHOTS_DIR = os.path.join(BASE_DIR, "assets", "headshots")

# ======================= #
# TEMPLATES               #
# ======================= #
TEMPLATES = [
    "👑 The Court honors {player} today.\n\nThey turn {age} as their reign continues. 🎂\n\n#NBA #CourtKingsHQ",
    "🎂 All rise for {player}.\n\nThe King celebrates {age} years of dominance. 👑\n\n#NBA #CourtKingsHQ",
    "📊 HQ Log > Birthday Event\n\nPlayer: {player}\n\nAge milestone: {age} 🎂\n\n#NBA #CourtKingsHQ",
    "🖥️ System Alert: {player} turns {age} today.\n\nTimeline updated. 👑\n\n#NBA #CourtKingsHQ",
    "⚡ Data Ping\n\nSubject: {player} | New Age: {age} 🎂\n\n#NBA #CourtKingsHQ"
]

# ======================= #
# HELPER FUNCTIONS        #
# ======================= #
def calculate_age(birthday_str):
    """birthday_str is in YYYY-MM-DD format"""
    try:
        bday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - bday.year - ((today.month, today.day) < (bday.month, bday.day))
        return age
    except Exception as e:
        print(f"⚠️ Error calculating age for {birthday_str}: {e}")
        return None

# ======================= #
# MAIN BOT LOGIC          #
# ======================= #
def main():
    today = date.today()
    today_str = today.strftime("%m-%d")  # format birthdays in MM-DD

    with open(BIRTHDAYS_JSON, "r", encoding="utf-8") as f:
        players = json.load(f)

    birthday_players = [p for p in players if p.get("birthday") == today_str]

    if not birthday_players:
        print("📭 No NBA birthdays today.")
        return

    for player in birthday_players:
        name = player["name"]
        pid = str(player["id"])
        full_bday = player.get("full_birthday")  # YYYY-MM-DD stored in JSON
        age = calculate_age(full_bday) if full_bday else "?"

        # Pick random template
        template = random.choice(TEMPLATES)
        tweet = template.format(player=name, age=age)

        image_path = os.path.join(HEADSHOTS_DIR, f"{pid}.png")

        print("\n=== TWEET PREVIEW ===\n")
        print(tweet)

        try:
            if os.path.exists(image_path):
                media = api_v1.media_upload(image_path)
                client.create_tweet(text=tweet, media_ids=[media.media_id])
                print(f"✅ Posted with image for {name}")
            else:
                client.create_tweet(text=tweet)
                print(f"✅ Posted without image (no headshot) for {name}")

        except Exception as e:
            print(f"❌ Error posting {name}: {e}")


if __name__ == "__main__":
    main()
