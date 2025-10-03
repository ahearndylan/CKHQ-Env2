import os
from datetime import datetime, date
import random
import tweepy

# ======================= #
# TWITTER AUTHENTICATION  #
# ======================= #
# Read from env (set these in GH Actions secrets or your local shell)
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


# v1.1 (handy if you attach media later)
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api_v1 = tweepy.API(auth)

# ======================= #
# COUNTDOWN CONFIG        #
# ======================= #
SEASON_START_DATE = os.getenv("NBA_SEASON_START_DATE", "2025-10-22")
BASE_HASHTAGS = "#NBA #CourtKingsHQ"

# Add an extra hype tag when close to tip-off
def extra_tag(days_left: int) -> str:
    if days_left <= 10 and days_left >= 1:
        return " #OpeningNight"
    return ""

# Morning vs Night rotating pools (short, punchy, and engagement-oriented)
AM_TEMPLATES = [
    "📡 HQ Protocol: Season startup in {X} days…\n\nAll stat engines warming up. ⚡\n\nWho’s your early MVP pick? 🏆\n\n{tags}",
    "👑 Royal Countdown: {X} days until the Court opens.\n\nNew season. New Kings.\n\nWhich team are you riding with this year? 🏀\n\n{tags}",
    "⏳ {X} days left…\n\nCourt Kings HQ booting Nightly, Efficiency, and Clutch trackers.\n\nDrop one bold prediction below. 🔮\n\n{tags}",
    "📊 System Log: {X} days remaining…\n\nCalibration in progress. Data feeds arming. ⚙️\n\nWhat matchup are you watching first? 👀\n\n{tags}",
]

PM_TEMPLATES = [
    "🖥️ HQ Uplink > {X} days until tip-off.\n\nStat monarchy resumes shortly. 👑\n\nWho claims the throne on Opening Night? 🏀\n\n{tags}",
    "🚨 Alert: Season launch in {X} days.\n\nCourt Kings HQ entering full-season mode.\n\nReply with your sleeper team. 😴➡️💥\n\n{tags}",
    "⚡ Countdown: {X} days…\n\nAll bots online. Reports ready.\n\nFirst 40-piece of the season comes from ____ ? 🍗🔥\n\n{tags}",
    "📈 Preseason Telemetry: {X} days to go.\n\nEngines stable. Fans restless.\n\nWhich rookie flashes first? 🍼✨\n\n{tags}",
]

OPENING_NIGHT_TEMPLATE = (
    "🎉 Opening Night is HERE!\n\n"
    "Court Kings HQ is live for our first full season. 👑\n\n"
    "{tags}"
)

# ======================= #
# UTIL                    #
# ======================= #
def local_hour() -> int:
    """
    Determine hour for AM/PM selection.
    Uses TZ if provided by runner (set TZ=America/New_York in workflow).
    """
    try:
        # GitHub Actions honors TZ env for strftime/localtime if set
        return datetime.now().hour
    except Exception:
        # Fallback to UTC hour
        return datetime.utcnow().hour

def pick_template(days_left: int) -> str:
    hr = local_hour()
    pool = AM_TEMPLATES if hr < 12 else PM_TEMPLATES
    # Make selection deterministic per half-day so AM/PM posts differ
    seed_val = int(f"{date.today().strftime('%Y%m%d')}{0 if hr < 12 else 1}")
    random.seed(seed_val)
    return random.choice(pool)

# ======================= #
# BUILD + POST            #
# ======================= #
def main():
    # Parse start date
    try:
        y, m, d = map(int, SEASON_START_DATE.split("-"))
        start_dt = date(y, m, d)
    except Exception as e:
        print(f"❌ Invalid SEASON_START_DATE '{SEASON_START_DATE}': {e}")
        return

    today = date.today()
    days_left = (start_dt - today).days

    if days_left < 0:
        print(f"ℹ️ Countdown finished (days_left={days_left}). Skipping.")
        return
    elif days_left == 0:
        tags = BASE_HASHTAGS + extra_tag(days_left)
        tweet = OPENING_NIGHT_TEMPLATE.format(tags=tags)
    else:
        template = pick_template(days_left)
        tags = BASE_HASHTAGS + extra_tag(days_left)
        tweet = template.format(X=days_left, tags=tags)

    # === Print preview ===
    print("\n=== TWEET PREVIEW (Bot 29 – Countdown) ===\n")
    print(tweet)

    # === Post ===
    try:
        if not all([bearer_token, api_key, api_secret, access_token, access_token_secret]):
            raise RuntimeError("Missing one or more X credentials in environment.")
        client.create_tweet(text=tweet)
        print("✅ Countdown tweet posted successfully!")
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")

if __name__ == "__main__":
    main()
