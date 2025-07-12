import json
import random
import os
import tweepy

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

# === File path setup ===
base_dir = os.path.dirname(os.path.abspath(__file__))
teams_path = os.path.join(base_dir, "teams.json")
used_file = os.path.join(base_dir, "used_matchups.json")

# === Load team data ===
with open(teams_path, "r") as f:
    teams = json.load(f)

# === Load used matchups ===
if os.path.exists(used_file):
    with open(used_file, "r") as f:
        used_matchups = json.load(f)
else:
    used_matchups = []

# === Helper to create matchup key ===
def matchup_key(team1, team2):
    return sorted([f"{team1['year']} {team1['short']}", f"{team2['year']} {team2['short']}"])

# === Select two valid, unused teams ===
max_attempts = 100
for _ in range(max_attempts):
    team1, team2 = random.sample(teams, 2)
    if team1["short"] == team2["short"]:
        continue
    matchup = matchup_key(team1, team2)
    if matchup not in used_matchups:
        break
else:
    print("❌ No valid matchups left.")
    exit()

# === Handle emoji collision (duplicate dots)
emoji1 = team1["emoji"]
emoji2 = team2["emoji"]
if isinstance(emoji1, list): emoji1 = emoji1[0]
if isinstance(emoji2, list): emoji2 = emoji2[0]
if emoji1 == emoji2 and isinstance(team2["emoji"], list) and len(team2["emoji"]) > 1:
    emoji2 = team2["emoji"][1]

# === Simulate series outcome ===
outcomes = [(4, 0), (4, 1), (4, 2), (4, 3)]
weights = [5, 15, 30, 50]
winner_score, loser_score = random.choices(outcomes, weights=weights)[0]
winner = random.choice([team1, team2])
loser = team1 if winner == team2 else team2

# === Generate Finals MVP stats ===
def random_stat(min_val, max_val, round_to=1):
    return round(random.uniform(min_val, max_val), round_to)

mvp = winner["star_player"]
ppg = random_stat(*winner["ppg_range"])
rpg = random_stat(4, 8)
apg = random_stat(3, 7)

if team1["short"] == team2["short"]:
    winner_name = f"{winner['year']} {winner['short']}"
else:
    winner_name = winner["short"]

total_games = winner_score + loser_score
tweet = f"""🏀 NBA 2K Sim – Dynasty Clash

{team1["year"]} {team1["team"]} {emoji1}
vs
{team2["year"]} {team2["team"]} {emoji2}

{winner_name} win the series in {total_games} games ({winner_score}–{loser_score})!

👑 Finals MVP: {mvp}
🏆 {ppg} PPG · {rpg} RPG · {apg} APG

#NBA2KSim #CourtKingsHQ
"""

# === Print tweet preview ===
print("\n=== TWEET PREVIEW ===\n")
print(tweet)

# === Save used matchup ===
used_matchups.append(matchup)
with open(used_file, "w") as f:
    json.dump(used_matchups, f, indent=2)

# === Post to Twitter ===
try:
    client.create_tweet(text=tweet)
    print("✅ Tweet posted successfully!")
except Exception as e:
    print(f"❌ Error posting tweet: {e}")
