"""
Builds one pass network per CLUB across every match that club played in a
dataset (not per match) - average touch positions and pass-edge counts
aggregated across all their matches, up to each match's first substitution.

Usage:
    python build_pass_network.py --dataset premier-league-2015-16
"""
import argparse
import json
import os
from collections import defaultdict

from datasets import DATASET_BY_ID

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "output")


def cached_match_ids(dataset_id):
    events_dir = os.path.join(DATA_DIR, dataset_id, "events")
    if not os.path.exists(events_dir):
        return []
    return [f.replace(".json", "") for f in os.listdir(events_dir) if f.endswith(".json")]


def first_sub_index(events, team_name):
    for e in events:
        if e["type"]["name"] == "Substitution" and e["team"]["name"] == team_name:
            return e["index"]
    return float("inf")


def build_networks(dataset_id):
    # club -> player -> [touch_x_sum, touch_y_sum, touch_count]
    touch_sum = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
    touch_count = defaultdict(lambda: defaultdict(int))
    # club -> (playerA, playerB) -> pass count
    edge_count = defaultdict(lambda: defaultdict(int))
    clubs_seen = set()

    for mid in cached_match_ids(dataset_id):
        with open(os.path.join(DATA_DIR, dataset_id, "events", f"{mid}.json")) as f:
            events = json.load(f)

        teams = sorted({e["team"]["name"] for e in events if "team" in e})
        cutoffs = {t: first_sub_index(events, t) for t in teams}

        for team in teams:
            clubs_seen.add(team)
            for e in events:
                if e.get("team", {}).get("name") != team:
                    continue
                if e["index"] >= cutoffs[team]:
                    continue
                if e["type"]["name"] != "Pass":
                    continue

                passer = e.get("player", {}).get("name")
                loc = e.get("location")
                pass_info = e.get("pass", {})
                recipient = pass_info.get("recipient", {}).get("name")
                outcome = pass_info.get("outcome")

                if passer and loc:
                    touch_sum[team][passer][0] += loc[0]
                    touch_sum[team][passer][1] += loc[1]
                    touch_count[team][passer] += 1

                if passer and recipient and outcome is None:
                    key = tuple(sorted([passer, recipient]))
                    edge_count[team][key] += 1

    networks = {}
    for club in clubs_seen:
        nodes = [
            {
                "player": p,
                "x": round(touch_sum[club][p][0] / touch_count[club][p], 1),
                "y": round(touch_sum[club][p][1] / touch_count[club][p], 1),
                "touches": touch_count[club][p],
            }
            for p in touch_count[club]
        ]
        edges = [
            {"players": list(k), "passes": v}
            for k, v in edge_count[club].items()
            if v >= 3
        ]
        # cap to the busiest players/edges so the diagram stays readable
        # when a club appears across many matches
        nodes = sorted(nodes, key=lambda n: -n["touches"])[:16]
        node_names = {n["player"] for n in nodes}
        edges = [e for e in edges if e["players"][0] in node_names and e["players"][1] in node_names]
        edges = sorted(edges, key=lambda e: -e["passes"])[:40]

        networks[club] = {"nodes": nodes, "edges": edges}

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"pass_network_{dataset_id}.json")
    with open(out_path, "w") as f:
        json.dump({"dataset_id": dataset_id, "clubs": networks}, f)

    print(f"Wrote pass networks for {len(networks)} clubs to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, choices=list(DATASET_BY_ID.keys()))
    args = parser.parse_args()
    build_networks(args.dataset)
