"""
Downloads every match's event data for a dataset (see datasets.py) from
StatsBomb's free open-data repo, and caches it to disk so re-running the
rest of the pipeline doesn't re-download everything.

Usage:
    python fetch_data.py --dataset premier-league-2015-16
    python fetch_data.py --dataset champions-league-finals
    python fetch_data.py --dataset premier-league-2015-16 --limit 20   # quick test run
"""
import argparse
import json
import os
import time

import requests

from datasets import DATASET_BY_ID

BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def fetch_json(path):
    r = requests.get(f"{BASE}/{path}", timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_dataset(dataset_id, limit=None):
    dataset = DATASET_BY_ID[dataset_id]
    out_dir = os.path.join(DATA_DIR, dataset_id)
    os.makedirs(os.path.join(out_dir, "events"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "lineups"), exist_ok=True)

    all_matches = []
    for comp_id, season_id in dataset["competitions"]:
        matches = fetch_json(f"matches/{comp_id}/{season_id}.json")
        all_matches.extend(matches)

    if limit:
        all_matches = all_matches[:limit]

    print(f"{dataset['label']}: {len(all_matches)} matches to fetch")

    match_index = []
    for i, m in enumerate(all_matches):
        mid = m["match_id"]
        events_path = os.path.join(out_dir, "events", f"{mid}.json")

        if not os.path.exists(events_path):
            try:
                events = fetch_json(f"events/{mid}.json")
                with open(events_path, "w") as f:
                    json.dump(events, f)
            except Exception as e:
                print(f"  [{i+1}/{len(all_matches)}] skipped {mid}: {e}")
                continue
            time.sleep(0.05)  # be polite to raw.githubusercontent.com

        match_index.append({
            "match_id": mid,
            "home_team": m["home_team"]["home_team_name"],
            "away_team": m["away_team"]["away_team_name"],
            "competition": m["competition"]["competition_name"],
            "season": m["season"]["season_name"],
            "match_date": m.get("match_date"),
        })
        if (i + 1) % 25 == 0:
            print(f"  fetched {i+1}/{len(all_matches)}")

    with open(os.path.join(out_dir, "match_index.json"), "w") as f:
        json.dump(match_index, f, indent=2)

    print(f"Done. {len(match_index)} matches cached in data/{dataset_id}/")
    return match_index


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, choices=list(DATASET_BY_ID.keys()))
    parser.add_argument("--limit", type=int, default=None, help="fetch only the first N matches, for a quick test run")
    args = parser.parse_args()
    fetch_dataset(args.dataset, limit=args.limit)
