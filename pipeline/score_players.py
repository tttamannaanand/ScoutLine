"""
Scores players as "value picks" by comparing their output (shots, xG,
goals per 90) against a market value figure, then normalizing to 0-100.

IMPORTANT: StatsBomb's open data does not include market values, and
Transfermarkt (the usual free source) isn't scrapeable from this
environment's network allowlist - so this script reads market values from
a plain CSV you fill in yourself: data/market_values.csv (columns: player,
value_eur_m). A handful of real, rounded example values for the sample
match's players are included to get you started; replace/extend as you
add more matches.

Usage:
    python score_players.py --match-id 3869685
"""
import argparse
import csv
import json
import os
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "output")
VALUES_CSV = os.path.join(DATA_DIR, "market_values.csv")


def load_market_values():
    values = {}
    if not os.path.exists(VALUES_CSV):
        return values
    with open(VALUES_CSV) as f:
        for row in csv.DictReader(f):
            values[row["player"]] = float(row["value_eur_m"])
    return values


def aggregate_player_stats(match_id):
    with open(os.path.join(DATA_DIR, f"events_{match_id}.json")) as f:
        events = json.load(f)

    stats = defaultdict(lambda: {"shots": 0, "goals": 0, "xg": 0.0, "team": None, "position": None})
    for e in events:
        if e["type"]["name"] != "Shot":
            continue
        name = e["player"]["name"]
        stats[name]["shots"] += 1
        stats[name]["xg"] += e["shot"]["statsbomb_xg"]
        stats[name]["team"] = e["team"]["name"]
        stats[name]["position"] = e.get("position", {}).get("name", "")
        if e["shot"]["outcome"]["name"] == "Goal":
            stats[name]["goals"] += 1

    return stats


def score_players(match_id):
    stats = aggregate_player_stats(match_id)
    values = load_market_values()

    rows = []
    for player, s in stats.items():
        value = values.get(player)
        if value is None or value <= 0:
            continue  # can't score without a value on file

        # simple heuristic: xG output per million euros of value, then
        # normalize to a 0-100 range across this player set. Swap this for
        # something more rigorous (e.g. per-90 across a full season) once
        # you have more than one match of data.
        output_per_value = s["xg"] / value
        rows.append({
            "player": player,
            "team": s["team"],
            "position": s["position"],
            "shots": s["shots"],
            "goals": s["goals"],
            "xg": round(s["xg"], 3),
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
    out_path = os.path.join(OUTPUT_DIR, f"player_scores_{match_id}.json")
    with open(out_path, "w") as f:
        json.dump({"match_id": match_id, "players": rows}, f, indent=2)

    print(f"Wrote {len(rows)} scored players to {out_path}")
    if not rows:
        print(f"No players matched market_values.csv - check {VALUES_CSV}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match-id", type=int, default=3869685)
    args = parser.parse_args()
    score_players(args.match_id)
