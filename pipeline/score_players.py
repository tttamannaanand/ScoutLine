"""
Aggregates each player's shot output ACROSS EVERY MATCH in a dataset
(proper per-90 numbers, not single-match totals), then scores them against
a market value figure from data/market_values.csv.

Usage:
    python score_players.py --dataset premier-league-2015-16
"""
import argparse
import csv
import json
import os
from collections import defaultdict

from datasets import DATASET_BY_ID

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "output")
VALUES_CSV = os.path.join(DATA_DIR, "market_values.csv")

DEFAULT_MINUTES_PER_APPEARANCE = 90  # StatsBomb open data doesn't always
# carry precise minutes played per player, so this is a simplifying
# assumption: treat every match a player has a shot event in as a full
# 90 minutes. Good enough for a portfolio demo; swap in real minutes-
# played data (from the lineup files' player stats) for real accuracy.


def load_market_values():
    values = {}
    if not os.path.exists(VALUES_CSV):
        return values
    with open(VALUES_CSV) as f:
        for row in csv.DictReader(f):
            values[row["player"]] = float(row["value_eur_m"])
    return values


def aggregate_players(dataset_id):
    events_dir = os.path.join(DATA_DIR, dataset_id, "events")
    stats = defaultdict(lambda: {
        "shots": 0, "goals": 0, "xg": 0.0, "matches": set(),
        "team": None, "position": None,
    })

    if not os.path.exists(events_dir):
        return stats

    for fname in os.listdir(events_dir):
        if not fname.endswith(".json"):
            continue
        mid = fname.replace(".json", "")
        with open(os.path.join(events_dir, fname)) as f:
            events = json.load(f)

        for e in events:
            if e["type"]["name"] != "Shot":
                continue
            name = e["player"]["name"]
            s = stats[name]
            s["shots"] += 1
            s["xg"] += e["shot"]["statsbomb_xg"]
            s["matches"].add(mid)
            s["team"] = e["team"]["name"]
            s["position"] = e.get("position", {}).get("name", "")
            if e["shot"]["outcome"]["name"] == "Goal":
                s["goals"] += 1

    return stats


def score_players(dataset_id):
    dataset = DATASET_BY_ID[dataset_id]
    stats = aggregate_players(dataset_id)
    values = load_market_values()

    rows = []
    for player, s in stats.items():
        value = values.get(player)
        if value is None or value <= 0:
            continue

        appearances = len(s["matches"])
        minutes = appearances * DEFAULT_MINUTES_PER_APPEARANCE
        xg_p90 = (s["xg"] / minutes) * 90 if minutes else 0
        output_per_value = xg_p90 / value

        rows.append({
            "player": player,
            "team": s["team"],
            "position": s["position"],
            "appearances": appearances,
            "shots": s["shots"],
            "goals": s["goals"],
            "xg_total": round(s["xg"], 2),
            "xg_p90": round(xg_p90, 3),
            "market_value_eur_m": value,
            "output_per_value": output_per_value,
        })

    if rows:
        max_opv = max(r["output_per_value"] for r in rows) or 1
        for r in rows:
            r["value_score"] = round(100 * r["output_per_value"] / max_opv, 1)
            del r["output_per_value"]

    rows.sort(key=lambda r: -r["value_score"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"player_scores_{dataset_id}.json")
    with open(out_path, "w") as f:
        json.dump({"dataset_id": dataset_id, "label": dataset["label"], "players": rows}, f)

    print(f"Wrote {len(rows)} scored players to {out_path}")
    if not rows:
        print(f"No players matched market_values.csv - check {VALUES_CSV}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, choices=list(DATASET_BY_ID.keys()))
    args = parser.parse_args()
    score_players(args.dataset)
