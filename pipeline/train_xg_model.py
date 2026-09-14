"""
Trains one xG model on shot distance/angle using every shot across BOTH
datasets pooled together (more training data = a steadier model), then
writes a shots file per dataset with each shot's modeled xG plus club/team
tags so the site can filter by club.

Usage:
    python train_xg_model.py --dataset premier-league-2015-16
    python train_xg_model.py --dataset champions-league-finals
"""
import argparse
import json
import math
import os

import numpy as np
from sklearn.linear_model import LogisticRegression

from datasets import DATASET_BY_ID

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "output")

GOAL_X, GOAL_Y = 120.0, 40.0
GOAL_WIDTH = 7.32


def shot_features(location):
    x, y = location[0], location[1]
    distance = math.hypot(GOAL_X - x, GOAL_Y - y)
    post1 = math.atan2(GOAL_Y - GOAL_WIDTH / 2 - y, GOAL_X - x)
    post2 = math.atan2(GOAL_Y + GOAL_WIDTH / 2 - y, GOAL_X - x)
    angle = abs(post1 - post2)
    return distance, angle


def cached_match_ids(dataset_id):
    events_dir = os.path.join(DATA_DIR, dataset_id, "events")
    if not os.path.exists(events_dir):
        return []
    return [f.replace(".json", "") for f in os.listdir(events_dir) if f.endswith(".json")]


def iter_shots(dataset_id):
    for mid in cached_match_ids(dataset_id):
        with open(os.path.join(DATA_DIR, dataset_id, "events", f"{mid}.json")) as f:
            events = json.load(f)
        for e in events:
            if e["type"]["name"] == "Shot":
                yield mid, e


def train_model():
    rows = []
    for dataset_id in DATASET_BY_ID:
        for _, e in iter_shots(dataset_id):
            if e["shot"]["type"]["name"] == "Penalty":
                continue
            distance, angle = shot_features(e["location"])
            goal = 1 if e["shot"]["outcome"]["name"] == "Goal" else 0
            rows.append((distance, angle, goal))

    print(f"Training on {len(rows)} pooled shots across all datasets")
    X = np.array([[d, a] for d, a, _ in rows])
    y = np.array([g for _, _, g in rows])
    model = LogisticRegression()
    model.fit(X, y)
    return model


def build_shot_data(dataset_id, model):
    dataset = DATASET_BY_ID[dataset_id]
    shots_out = []

    for mid, e in iter_shots(dataset_id):
        distance, angle = shot_features(e["location"])
        our_xg = float(model.predict_proba([[distance, angle]])[0][1])
        shots_out.append({
            "match_id": mid,
            "player": e["player"]["name"],
            "team": e["team"]["name"],
            "minute": e["minute"],
            "location": e["location"],
            "outcome": e["shot"]["outcome"]["name"],
            "is_goal": e["shot"]["outcome"]["name"] == "Goal",
            "body_part": e["shot"]["body_part"]["name"],
            "statsbomb_xg": round(e["shot"]["statsbomb_xg"], 3),
            "our_xg": round(our_xg, 3),
        })

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"shots_{dataset_id}.json")
    with open(out_path, "w") as f:
        json.dump({
            "dataset_id": dataset_id,
            "label": dataset["label"],
            "matches_included": len(cached_match_ids(dataset_id)),
            "shots": shots_out,
        }, f)

    print(f"Wrote {len(shots_out)} shots to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, choices=list(DATASET_BY_ID.keys()))
    args = parser.parse_args()

    model = train_model()
    build_shot_data(args.dataset, model)
