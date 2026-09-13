"""
Trains a simple expected-goals (xG) model from shot location, and writes
the shot map JSON for a single match that the website reads.

Model: logistic regression on distance-to-goal-center and shot angle.
This is intentionally simple (StatsBomb's own xG uses many more features -
defender positions, shot technique, etc) but it's enough to demonstrate the
concept end to end, and you can explain the tradeoff in your README.

Pitch dimensions in StatsBomb data: 120 x 80 yards. Goal center is at
(120, 40).

Usage:
    python train_xg_model.py --match-id 3869685
"""
import argparse
import json
import math
import os

import numpy as np
from sklearn.linear_model import LogisticRegression

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "output")

GOAL_X, GOAL_Y = 120.0, 40.0
GOAL_WIDTH = 7.32


def shot_features(location):
    x, y = location[0], location[1]
    dx = GOAL_X - x
    dy = GOAL_Y - y
    distance = math.hypot(dx, dy)

    # angle subtended by the goal mouth from the shot location
    post1 = math.atan2(GOAL_Y - GOAL_WIDTH / 2 - y, GOAL_X - x)
    post2 = math.atan2(GOAL_Y + GOAL_WIDTH / 2 - y, GOAL_X - x)
    angle = abs(post1 - post2)

    return distance, angle


def load_all_open_data_shots(sample_match_ids):
    """Pull a handful of matches to get enough shots to fit a model on.
    For a real project you'd train on hundreds of matches; this keeps the
    demo fast. Falls back gracefully if a match fetch fails."""
    import requests
    BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
    rows = []
    for mid in sample_match_ids:
        try:
            events = requests.get(f"{BASE}/events/{mid}.json", timeout=30).json()
        except Exception as e:
            print(f"  skipped match {mid}: {e}")
            continue
        for e in events:
            if e["type"]["name"] != "Shot":
                continue
            if e["shot"]["type"]["name"] == "Penalty":
                continue  # penalties are near-constant probability, skip for training
            distance, angle = shot_features(e["location"])
            goal = 1 if e["shot"]["outcome"]["name"] == "Goal" else 0
            rows.append((distance, angle, goal))
    return rows


def train_model():
    # A handful of 2022 World Cup knockout matches for training data variety
    training_match_ids = [3869685, 3869519, 3869354, 3857256, 3869151]
    print("Pulling training shots from open-data matches...")
    rows = load_all_open_data_shots(training_match_ids)
    print(f"Collected {len(rows)} training shots")

    X = np.array([[d, a] for d, a, _ in rows])
    y = np.array([g for _, _, g in rows])

    model = LogisticRegression()
    model.fit(X, y)
    return model


def build_shot_map(match_id, model):
    with open(os.path.join(DATA_DIR, f"events_{match_id}.json")) as f:
        events = json.load(f)

    shots_out = []
    for e in events:
        if e["type"]["name"] != "Shot":
            continue
        distance, angle = shot_features(e["location"])
        our_xg = float(model.predict_proba([[distance, angle]])[0][1])

        shots_out.append({
            "player": e["player"]["name"],
            "team": e["team"]["name"],
            "minute": e["minute"],
            "location": e["location"],  # [x, y] in 0-120 / 0-80 pitch coords
            "outcome": e["shot"]["outcome"]["name"],
            "is_goal": e["shot"]["outcome"]["name"] == "Goal",
            "body_part": e["shot"]["body_part"]["name"],
            "statsbomb_xg": round(e["shot"]["statsbomb_xg"], 3),
            "our_xg": round(our_xg, 3),
        })

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"shots_{match_id}.json")
    with open(out_path, "w") as f:
        json.dump({"match_id": match_id, "shots": shots_out}, f, indent=2)

    print(f"Wrote {len(shots_out)} shots to {out_path}")
    return shots_out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match-id", type=int, default=3869685)
    args = parser.parse_args()

    model = train_model()
    build_shot_map(args.match_id, model)
