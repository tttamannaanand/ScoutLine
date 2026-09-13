"""
Downloads a match's event data from StatsBomb's free open-data repo.

StatsBomb open data covers a set of competitions (men's and women's World
Cups, Euros, some domestic league seasons, etc). No API key needed - it's
just JSON files on GitHub. Data is licensed for non-commercial / educational
use - credit StatsBomb wherever you show the data (see site/about.html).

Usage:
    python fetch_data.py                     # fetches the default sample match
    python fetch_data.py --match-id 3869685   # fetch a specific match
    python fetch_data.py --list-competitions  # see what's available
"""
import argparse
import json
import os
import requests

BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# 2022 World Cup Final, Argentina vs France - good default: dramatic match,
# lots of shots, well known, so pass network / shot map screenshots make sense
# to anyone looking at your profile without extra context.
DEFAULT_MATCH_ID = 3869685


def fetch_json(path):
    url = f"{BASE}/{path}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def list_competitions():
    comps = fetch_json("competitions.json")
    seen = set()
    for c in comps:
        key = (c["competition_name"], c["season_name"])
        if key not in seen:
            seen.add(key)
            print(f"{c['competition_id']:>4}  {c['season_id']:>4}  {c['competition_name']} - {c['season_name']}")


def fetch_match(match_id):
    os.makedirs(DATA_DIR, exist_ok=True)

    events = fetch_json(f"events/{match_id}.json")
    lineups = fetch_json(f"lineups/{match_id}.json")

    with open(os.path.join(DATA_DIR, f"events_{match_id}.json"), "w") as f:
        json.dump(events, f)
    with open(os.path.join(DATA_DIR, f"lineups_{match_id}.json"), "w") as f:
        json.dump(lineups, f)

    print(f"Saved {len(events)} events and lineup data for match {match_id} to /data")
    return events, lineups


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match-id", type=int, default=DEFAULT_MATCH_ID)
    parser.add_argument("--list-competitions", action="store_true")
    args = parser.parse_args()

    if args.list_competitions:
        list_competitions()
    else:
        fetch_match(args.match_id)
