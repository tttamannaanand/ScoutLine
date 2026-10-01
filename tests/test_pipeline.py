import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))

import score_players  # noqa: E402
import train_xg_model  # noqa: E402
from datasets import DATASET_BY_ID, DATASETS  # noqa: E402
from train_xg_model import GOAL_X, GOAL_Y, shot_features  # noqa: E402

# --- shot geometry ---------------------------------------------------------


def test_penalty_spot_distance_and_angle():
    distance, angle = shot_features([GOAL_X - 12, GOAL_Y])
    assert distance == pytest.approx(12)
    # Full goal mouth seen from the spot: 2 * atan(3.66 / 12)
    assert angle == pytest.approx(2 * math.atan(3.66 / 12))


def test_angle_is_symmetric_about_goal_centre():
    _, left = shot_features([100, GOAL_Y - 10])
    _, right = shot_features([100, GOAL_Y + 10])
    assert left == pytest.approx(right)


def test_closer_central_shots_see_more_goal():
    near = shot_features([110, GOAL_Y])
    far = shot_features([90, GOAL_Y])
    wide = shot_features([110, GOAL_Y + 25])
    assert near[0] < far[0]
    assert near[1] > far[1]
    assert near[1] > wide[1]


# --- xG model ---------------------------------------------------------------


def test_model_learns_that_close_shots_score_more():
    rng = np.random.default_rng(0)
    xs = rng.uniform(85, 118, 4000)
    feats = np.array([shot_features([x, GOAL_Y]) for x in xs])
    p_goal = 1 / (1 + np.exp(0.25 * (feats[:, 0] - 12)))
    goals = (rng.uniform(size=len(xs)) < p_goal).astype(int)

    from sklearn.linear_model import LogisticRegression

    model = LogisticRegression().fit(feats, goals)

    close = model.predict_proba([shot_features([114, GOAL_Y])])[0][1]
    far = model.predict_proba([shot_features([90, GOAL_Y])])[0][1]
    assert close > far


# --- player scoring ---------------------------------------------------------


def _shot(player, team, xg, goal=False):
    return {
        "type": {"name": "Shot"},
        "player": {"name": player},
        "team": {"name": team},
        "position": {"name": "Forward"},
        "shot": {"statsbomb_xg": xg, "outcome": {"name": "Goal" if goal else "Saved"}},
    }


@pytest.fixture
def fake_data(tmp_path, monkeypatch):
    ds = "premier-league-2015-16"
    events = tmp_path / ds / "events"
    events.mkdir(parents=True)
    (events / "1.json").write_text(
        json.dumps(
            [
                _shot("Cheap", "A", 0.5, goal=True),
                _shot("Pricey", "B", 0.5),
                {"type": {"name": "Pass"}},
            ]
        )
    )
    (events / "2.json").write_text(json.dumps([_shot("Cheap", "A", 0.3)]))
    (tmp_path / "market_values.csv").write_text("player,value_eur_m\nCheap,5\nPricey,50\n")
    out = tmp_path / "out"
    monkeypatch.setattr(score_players, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(score_players, "VALUES_CSV", str(tmp_path / "market_values.csv"))
    monkeypatch.setattr(score_players, "OUTPUT_DIR", str(out))
    return ds, out


def test_aggregate_counts_shots_goals_and_matches(fake_data):
    ds, _ = fake_data
    stats = score_players.aggregate_players(ds)
    assert stats["Cheap"]["shots"] == 2
    assert stats["Cheap"]["goals"] == 1
    assert stats["Cheap"]["xg"] == pytest.approx(0.8)
    assert len(stats["Cheap"]["matches"]) == 2


def test_value_score_ranks_cheap_output_first(fake_data):
    ds, out = fake_data
    score_players.score_players(ds)
    players = json.loads((out / f"player_scores_{ds}.json").read_text())["players"]
    assert [p["player"] for p in players] == ["Cheap", "Pricey"]
    assert players[0]["value_score"] == 100.0
    # Cheap: 0.4 xG/90 / €5m vs Pricey: 0.5 xG/90 / €50m -> 0.08 vs 0.01
    assert players[1]["value_score"] == pytest.approx(12.5)


# --- dataset registry -------------------------------------------------------


def test_dataset_ids_are_unique_and_indexed():
    assert len(DATASET_BY_ID) == len(DATASETS)
    for d in DATASETS:
        assert d["competitions"], d["id"]


def test_train_module_points_at_repo_paths():
    assert train_xg_model.OUTPUT_DIR.endswith(str(Path("site") / "output"))
