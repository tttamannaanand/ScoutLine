#!/usr/bin/env bash
# Fetches StatsBomb data and rebuilds every JSON file the site reads.
# Usage: ./run_pipeline.sh            (all datasets)
#        ./run_pipeline.sh --limit 5  (quick smoke run: 5 matches each)
set -euo pipefail
cd "$(dirname "$0")/pipeline"

DATASETS=$(python -c "from datasets import DATASETS; print(' '.join(d['id'] for d in DATASETS))")

for ds in $DATASETS; do
  python fetch_data.py --dataset "$ds" "$@"
done
for ds in $DATASETS; do
  python train_xg_model.py --dataset "$ds"
  python build_pass_network.py --dataset "$ds"
  python score_players.py --dataset "$ds"
done
python build_datasets_index.py
