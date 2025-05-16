from nba_api.stats.endpoints import playercareerstats
from time import sleep
import math
import tweepy
import random
from supabase import create_client, Client
from datetime import date

# === Supabase Credentials ===
url = "https://fjtxowbjnxclzcogostk.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZqdHhvd2JqbnhjbHpjb2dvc3RrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2MDE5NTgsImV4cCI6MjA1ODE3Nzk1OH0.LPkFw-UX6io0F3j18Eefd1LmeAGGXnxL4VcCLOR_c1Q"
supabase: Client = create_client(url, key)

# === Twitter Auth ===
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

# === Top Players List ===
top_players = [
    {"name": "LeBron James", "id": 2544},
    {"name": "Stephen Curry", "id": 201939},
    {"name": "Kevin Durant", "id": 201142},
    {"name": "Chris Paul", "id": 101108},
    {"name": "James Harden", "id": 201935},
    {"name": "Russell Westbrook", "id": 201566},
    {"name": "Damian Lillard", "id": 203081},
    {"name": "DeMar DeRozan", "id": 201942},
    {"name": "Klay Thompson", "id": 202691},
    {"name": "Kyrie Irving", "id": 202681},
    {"name": "Kevin Love", "id": 201567},
    {"name": "Brook Lopez", "id": 201572},
    {"name": "Paul George", "id": 202331},
    {"name": "Jimmy Butler", "id": 202710},
    {"name": "Anthony Davis", "id": 203076},
    {"name": "Giannis Antetokounmpo", "id": 203507},
    {"name": "Joel Embiid", "id": 203954},
    {"name": "Jayson Tatum", "id": 1628369},
    {"name": "Jaylen Brown", "id": 1627759},
    {"name": "Nikola Jokic", "id": 203999},
    {"name": "Luka Doncic", "id": 1629029},
    {"name": "Devin Booker", "id": 1626164},
    {"name": "Donovan Mitchell", "id": 1628378},
    {"name": "Julius Randle", "id": 203944},
    {"name": "Zach LaVine", "id": 203897},
    {"name": "Trae Young", "id": 1629027},
    {"name": "Ja Morant", "id": 1629630},
    {"name": "Tyrese Haliburton", "id": 1630169},
    {"name": "Domantas Sabonis", "id": 1627734},
    {"name": "Bam Adebayo", "id": 1628389},
    {"name": "CJ McCollum", "id": 203468},
    {"name": "Bradley Beal", "id": 203078},
    {"name": "Fred VanVleet", "id": 1627832},
    {"name": "Jrue Holiday", "id": 201950},
    {"name": "Tobias Harris", "id": 202699},
    {"name": "Kristaps Porzingis", "id": 204001},
    {"name": "Mikal Bridges", "id": 1628960},
    {"name": "Michael Porter Jr.", "id": 1629008},
    {"name": "Jamal Murray", "id": 1627750},
    {"name": "D'Angelo Russell", "id": 1626156},
    {"name": "Derrick White", "id": 1628401},
    {"name": "Aaron Gordon", "id": 203932},
    {"name": "Terry Rozier", "id": 1626179},
    {"name": "Malik Monk", "id": 1628370},
    {"name": "Kyle Kuzma", "id": 1628398},
    {"name": "Buddy Hield", "id": 1627741},
    {"name": "Andrew Wiggins", "id": 203952},
    {"name": "Jaren Jackson Jr.", "id": 1628991},
    {"name": "Desmond Bane", "id": 1630217}
]

# === Milestone Criteria ===
milestones = {
    "PTS": {"label": "points", "min": 10000, "step": 1000},
    "AST": {"label": "assists", "min": 1000, "step": 500},
    "REB": {"label": "rebounds", "min": 1000, "step": 500},
    "FG3M": {"label": "3-pointers", "min": 500, "step": 250}
}

print(f"👑⏳ Milestone Watch – Scanning {len(top_players)} stars...\n")

milestone_tweets = []

# === Loop through players ===
for p in top_players:
    try:
        data = playercareerstats.PlayerCareerStats(player_id=p["id"])
        df = data.get_data_frames()[0]
        df = df[df["SEASON_ID"].str.startswith("2")]

        totals = {
            "PTS": int(df["PTS"].sum()),
            "AST": int(df["AST"].sum()),
            "REB": int(df["REB"].sum()),
            "FG3M": int(df["FG3M"].sum())
        }

        for stat, info in milestones.items():
            val = totals[stat]
            if val >= info["min"]:
                step = info["step"]
                next_milestone = math.ceil(val / step) * step
                distance = next_milestone - val

                if 0 < distance <= 100:
                    # === Check Supabase ===
                    existing = supabase.table("milestone_watch") \
                        .select("*") \
                        .eq("player_name", p["name"]) \
                        .eq("stat_type", stat) \
                        .eq("milestone", next_milestone) \
                        .execute()

                    if existing.data:
                        continue  # already posted

                    tweet = f"""👑⏳ Milestone Watch

{p['name']} is {distance} away from {next_milestone} career {info['label']}.

#NBA #{p['name'].replace(' ', '')} #MilestoneWatch #CourtKingsHQ"""

                    milestone_tweets.append({
                        "tweet": tweet,
                        "player_name": p["name"],
                        "stat_type": stat,
                        "milestone": next_milestone
                    })

    except Exception as e:
        print(f"❌ Error for {p['name']}: {e}")

    sleep(1)

# === Post one milestone tweet if available ===
if milestone_tweets:
    selected = random.choice(milestone_tweets)
    print("\n=== TWEET PREVIEW ===\n")
    print(selected["tweet"])

    try:
        client.create_tweet(text=selected["tweet"])
        print("✅ Tweet posted successfully!")

        # Save to Supabase
        supabase.table("milestone_watch").insert({
            "player_name": selected["player_name"],
            "stat_type": selected["stat_type"],
            "milestone": selected["milestone"],
            "posted_date": str(date.today())
        }).execute()

    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
else:
    print("📭 No milestone tweets to post today.")
