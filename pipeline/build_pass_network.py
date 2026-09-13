"""
Builds a pass network for each team in a match: every player as a node
positioned at their average touch location, with edges weighted by how
many completed passes went between each pair of players.

Only counts passes up to each team's first substitution, which is the
standard convention (a sub changes the shape, so mixing minutes muddies
the picture).

Usage:
    python build_pass_network.py --match-id 3869685
"""
import argparse
import json
import os
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "output")


def first_sub_index(events, team_name):
    for e in events:
        if e["type"]["name"] == "Substitution" and e["team"]["name"] == team_name:
            return e["index"]
    return float("inf")


def build_network(match_id):
    with open(os.path.join(DATA_DIR, f"events_{match_id}.json")) as f:
        events = json.load(f)

    teams = sorted({e["team"]["name"] for e in events if "team" in e})
    cutoffs = {t: first_sub_index(events, t) for t in teams}

    networks = {}
    for team in teams:
        touch_sum = defaultdict(lambda: [0.0, 0.0])
        touch_count = defaultdict(int)
        edge_count = defaultdict(int)

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
            outcome = pass_info.get("outcome")  # present only if incomplete

            if passer and loc:
                touch_sum[passer][0] += loc[0]
                touch_sum[passer][1] += loc[1]
                touch_count[passer] += 1

            if passer and recipient and outcome is None:  # None outcome = completed
                key = tuple(sorted([passer, recipient]))
                edge_count[key] += 1

        nodes = [
            {
                "player": p,
                "x": round(touch_sum[p][0] / touch_count[p], 1),
                "y": round(touch_sum[p][1] / touch_count[p], 1),
                "touches": touch_count[p],
            }
            for p in touch_count
        ]
        edges = [
            {"players": list(k), "passes": v}
            for k, v in edge_count.items()
            if v >= 2  # drop one-off passes to keep the diagram readable
        ]

        networks[team] = {"nodes": nodes, "edges": edges}

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"pass_network_{match_id}.json")
    with open(out_path, "w") as f:
        json.dump({"match_id": match_id, "teams": networks}, f, indent=2)

    print(f"Wrote pass networks for {list(networks.keys())} to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match-id", type=int, default=3869685)
    args = parser.parse_args()
    build_network(args.match_id)
