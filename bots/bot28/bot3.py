# bots/bot3.py
import os, json, hashlib, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any
import requests

DATA_PATH = os.getenv("BIRTHDAY_JSON", "players_birthdays.json")
OUT_DIR = os.getenv("HEADSHOT_CACHE_DIR", "assets/headshots")
MAX_WORKERS = int(os.getenv("HEADSHOT_WORKERS", "6"))
RETRIES = int(os.getenv("HEADSHOT_RETRIES", "3"))
TIMEOUT = float(os.getenv("HEADSHOT_TIMEOUT", "10"))
SLEEP_BETWEEN_RETRIES = float(os.getenv("HEADSHOT_RETRY_SLEEP", "0.8"))
MANIFEST_PATH = os.getenv("HEADSHOT_MANIFEST", "assets/headshots_manifest.json")

HEADSHOT_URL = "https://cdn.nba.com/headshots/nba/latest/1040x760/{pid}.png"

os.makedirs(OUT_DIR, exist_ok=True)

def load_players() -> list[Dict[str, Any]]:
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def file_path(pid: int) -> str:
    return os.path.join(OUT_DIR, f"{pid}.png")

def sha1_of_bytes(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()

def download_one(pid: int, name: str) -> Dict[str, Any]:
    target = file_path(pid)
    if os.path.exists(target) and os.path.getsize(target) > 1024:
        return {"id": pid, "name": name, "status": "cached", "path": target}

    url = HEADSHOT_URL.format(pid=pid)
    last_err = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, timeout=TIMEOUT)
            if not r.ok or len(r.content) < 1024:
                last_err = f"bad response (code={r.status_code}, size={len(r.content)})"
            else:
                with open(target, "wb") as f:
                    f.write(r.content)
                return {
                    "id": pid,
                    "name": name,
                    "status": "downloaded",
                    "path": target,
                    "bytes": len(r.content),
                    "sha1": sha1_of_bytes(r.content),
                }
        except Exception as e:
            last_err = str(e)
        if attempt < RETRIES:
            time.sleep(SLEEP_BETWEEN_RETRIES)

    return {"id": pid, "name": name, "status": "failed", "error": last_err, "url": url}

def main():
    try:
        players = load_players()
    except Exception as e:
        print(f"❌ Could not read {DATA_PATH}: {e}")
        return

    # dedupe by id (if your JSON mixes active/retired, this avoids dup work)
    seen = set()
    unique = []
    for p in players:
        pid = int(p["id"])
        if pid not in seen:
            seen.add(pid)
            unique.append({"id": pid, "name": p["name"]})

    print(f"🧰 Headshot cache build: {len(unique)} players")
    results = []
    ok = 0
    cached = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(download_one, p["id"], p["name"]): p for p in unique}
        for fut in as_completed(futs):
            res = fut.result()
            results.append(res)
            if res["status"] == "downloaded":
                ok += 1
                print(f"✅ {res['name']} ({res['id']}) downloaded → {os.path.basename(res['path'])}")
            elif res["status"] == "cached":
                cached += 1
                # keep logs light
            else:
                failed += 1
                print(f"⚠️ {res['name']} ({res['id']}) failed: {res.get('error')}")

    # Write manifest
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(
            {
                "generated_at": int(time.time()),
                "input_json": DATA_PATH,
                "output_dir": OUT_DIR,
                "stats": {"downloaded": ok, "cached": cached, "failed": failed, "total": len(unique)},
                "results": results,
            },
            f,
            indent=2,
        )

    print(f"\n📦 Done. downloaded={ok}, cached={cached}, failed={failed}, total={len(unique)}")
    print(f"📝 Manifest → {MANIFEST_PATH}")

if __name__ == "__main__":
    main()
