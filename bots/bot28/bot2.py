# scripts/build_birthdays_json.py
import json, time
from nba_api.stats.static import players as static_players
from nba_api.stats.endpoints import commonplayerinfo

ACTIVE_ONLY = True  # set False if you want every historical player
SLEEP_BETWEEN_CALLS = 0.6  # be polite to the API

def fetch_birthdate(player_id: int) -> str | None:
    try:
        info = commonplayerinfo.CommonPlayerInfo(player_id=player_id, timeout=10)
        df = info.get_data_frames()[0]
        # BIRTHDATE like '1984-12-30T00:00:00' (UTC). Keep ISO string, or strip time.
        return str(df.loc[0, "BIRTHDATE"]).split("T")[0]
    except Exception as e:
        print(f"warn: {player_id} -> {e}")
        return None

def main():
    plist = static_players.get_players()  # [{'id', 'full_name', 'is_active'}, ...]
    if ACTIVE_ONLY:
        plist = [p for p in plist if p.get("is_active")]

    out = []
    for i, p in enumerate(plist, 1):
        pid = p["id"]
        bday = fetch_birthdate(pid)
        if bday:
            out.append({
                "id": pid,
                "name": p["full_name"],
                "birthdate": bday,               # 'YYYY-MM-DD'
                "is_active": bool(p.get("is_active")),
                "headshot": f"https://cdn.nba.com/headshots/nba/latest/1040x760/{pid}.png"
            })
        if i % 25 == 0:
            print(f"{i}/{len(plist)} processed...")
        time.sleep(SLEEP_BETWEEN_CALLS)

    with open("players_birthdays.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote players_birthdays.json with {len(out)} players.")

if __name__ == "__main__":
    main()
