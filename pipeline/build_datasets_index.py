"""
Writes site/output/datasets_index.json - a small summary of each dataset
(label, clubs, match/shot counts) that the site reads to populate the
competition picker and the top stat row, without needing to load the full
shot/network files just to know what's available.

Run this LAST, after the other three pipeline scripts, for each dataset.

Usage:
    python build_datasets_index.py
"""
import json
import os

from datasets import DATASETS

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "output")


def summarize(dataset_id):
    shots_path = os.path.join(OUTPUT_DIR, f"shots_{dataset_id}.json")
    network_path = os.path.join(OUTPUT_DIR, f"pass_network_{dataset_id}.json")
    players_path = os.path.join(OUTPUT_DIR, f"player_scores_{dataset_id}.json")

    summary = {"matches": 0, "clubs": 0, "shots": 0, "players_scored": 0}

    if os.path.exists(shots_path):
        with open(shots_path) as f:
            shots_data = json.load(f)
        summary["matches"] = shots_data.get("matches_included", 0)
        summary["shots"] = len(shots_data.get("shots", []))

    if os.path.exists(network_path):
        with open(network_path) as f:
            net_data = json.load(f)
        clubs = sorted(net_data.get("clubs", {}).keys())
        summary["clubs"] = len(clubs)
        summary["club_list"] = clubs

    if os.path.exists(players_path):
        with open(players_path) as f:
            players_data = json.load(f)
        summary["players_scored"] = len(players_data.get("players", []))

    return summary


def main():
    index = []
    for d in DATASETS:
        s = summarize(d["id"])
        index.append({
            "id": d["id"],
            "label": d["label"],
            "short_label": d["short_label"],
            **s,
        })

    with open(os.path.join(OUTPUT_DIR, "datasets_index.json"), "w") as f:
        json.dump({"datasets": index}, f, indent=2)

    print("Wrote datasets_index.json")
    for d in index:
        print(f"  {d['label']}: {d['clubs']} clubs, {d['matches']} matches, {d['shots']} shots")


if __name__ == "__main__":
    main()
