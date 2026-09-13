# Scoutline

A small football analytics site: an xG model, a pass network visualizer, and
a player value explorer, built on one shared pipeline over StatsBomb's free
open match data.

Default sample match: **Argentina vs France, 2022 World Cup Final**.

**Live structure**
- `pipeline/` — Python scripts that pull match data and precompute the JSON the site reads
- `site/` — the static website (plain HTML/CSS/JS, no framework, no backend)
- `site/output/` — precomputed JSON the pipeline writes and the site fetches
- `data/` — raw downloaded match data + the market values CSV

## How it works

The site never talks to a live API or runs Python. Everything is
precomputed once, offline, into JSON files that plain `fetch()` calls load.
That means the whole thing is static and free to host.

```
StatsBomb open data  →  pipeline/*.py  →  site/output/*.json  →  site (fetch + render)
```

## Running the pipeline

```bash
cd pipeline
pip install -r requirements.txt

python fetch_data.py                        # downloads the default match's event + lineup data
python train_xg_model.py --match-id 3869685  # trains the xG model, writes shots_<id>.json
python build_pass_network.py --match-id 3869685
python score_players.py --match-id 3869685
```

To use a different match, find its `match_id` from StatsBomb's open-data
repo (`python fetch_data.py --list-competitions` lists what's available),
then re-run all four commands with `--match-id <id>`. Update `MATCH_ID` in
`site/js/shotmap.js`, `passnetwork.js`, and `players.js` to match.

### Market values

StatsBomb's open data has no transfer-value field, and the usual free
source (Transfermarkt) isn't easily scraped from most sandboxed
environments. `score_players.py` reads market values from
`data/market_values.csv` instead — a plain two-column file
(`player,value_eur_m`) you fill in yourself. The included file has sample
values for this match's players; treat them as illustrative, not live
figures, and swap in real ones if accuracy matters for what you're using
this for.

## Running the site locally

```bash
cd site
python3 -m http.server 8000
# open http://localhost:8000
```

## Deploying

**Vercel** (recommended): push this repo to GitHub, import it in Vercel,
and it picks up `vercel.json`'s `outputDirectory: site` automatically — no
build step needed since it's static files. You'll get a live
`yourproject.vercel.app` URL.

**GitHub Pages**: also works — set Pages to serve from the `site/` folder
(or move `site/`'s contents to the repo root if you'd rather not configure
a subfolder).

## Data credit

Match data is from [StatsBomb's open data](https://github.com/statsbomb/open-data),
free for non-commercial and educational use. Credit StatsBomb wherever you
show this data (see `site/about.html` for the wording used here).

## Extending this

- Swap the logistic regression in `train_xg_model.py` for a gradient-boosted
  model (`xgboost`/`lightgbm`) and more features (shot technique, defender
  proximity from the freeze frame data) for a real accuracy jump.
- Run the pipeline across a full competition instead of one match, and
  aggregate player stats to per-90 instead of single-match totals — much
  more meaningful for the value score.
- Add a match picker to the site instead of hardcoding `MATCH_ID`, once
  you've precomputed JSON for more than one match.
