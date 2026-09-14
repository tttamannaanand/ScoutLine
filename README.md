<div align="center">

# ⚽ Scoutline

**A club football scouting toolkit built from scratch: an xG model, pass network visualizer, and undervalued-player finder — all running on one shared pipeline over real match data.**

[![Made with Python](https://img.shields.io/badge/pipeline-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Vanilla JS](https://img.shields.io/badge/frontend-HTML%20%2F%20CSS%20%2F%20JS-F7DF1E?logo=javascript&logoColor=black)](https://developer.mozilla.org/)
[![Data: StatsBomb](https://img.shields.io/badge/data-StatsBomb%20open--data-1DA462)](https://github.com/statsbomb/open-data)
[![Deploy: Vercel](https://img.shields.io/badge/deploy-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com)

[Live demo](#) · [Report a bug](../../issues) · [Methodology](site/about.html)

</div>

---

## What is this

Scoutline turns raw football event data into three things scouts and analysts actually look at, across **five real competitions** — switch between them from the sidebar:

| | |
|---|---|
| 🎯 **Shot map** | Every shot in a competition, plotted on the pitch and sized by a from-scratch expected-goals (xG) model |
| 🕸️ **Pass network** | Each club's shape and passing chemistry, built from average touch positions and pass-frequency edges |
| 💰 **Player explorer** | Shot output per 90 minutes weighed against market value, to surface who's punching above their price tag |

No backend, no live API calls, no framework. The Python pipeline crunches the data once and writes plain JSON; the website is static HTML/CSS/JS that fetches it. That means it's free to host and fast to load.

## Datasets

| Competition | Coverage | Clubs | Shots |
|---|---|---|---|
| **Premier League 2015/16** | Full season — all 380 matches | 20 | 9,908 |
| **La Liga 2015/16** | Full season — all 380 matches | 20 | 9,168 |
| **Ligue 1 2015/16** | Full season — 377 of 380 matches | 22 | 8,814 |
| **Serie A 2015/16** | Full season — all 380 matches | 20 | 9,998 |
| **Champions League finals** | Every final StatsBomb has released, 1970–2019 | 17 across 18 finals | 594 |

> **Why these five, and why 2015/16 shows up everywhere:** StatsBomb's free open data only ships *complete* seasons for a handful of competition/year combinations — most other seasons are partial single-club releases. 2015/16 happens to be the year with full-season coverage across four of Europe's top leagues, so that's what's here. Bundesliga and MLS were left out rather than shipped with misleading partial data — see [`site/about.html`](site/about.html) for the full breakdown, including the Champions League finals-only caveat.

## How it works

```
StatsBomb open data  →  pipeline/*.py  →  site/output/*.json  →  static site (fetch + render)
```

Everything is precomputed offline into JSON. The site never runs Python or talks to a live API — it's pure `fetch()` calls against files sitting next to it, which is what makes it deployable on Vercel/GitHub Pages with zero backend. The xG model is trained once on all ~38,000 shots pooled across every dataset, then applied per-competition.

## Quickstart

```bash
git clone https://github.com/<your-username>/scoutline.git
cd scoutline/pipeline
pip install -r requirements.txt

# pull match data for every dataset (see pipeline/datasets.py for the list)
for ds in premier-league-2015-16 la-liga-2015-16 ligue-1-2015-16 serie-a-2015-16 champions-league-finals; do
  python fetch_data.py --dataset $ds
done

# build the site's JSON for each dataset
for ds in premier-league-2015-16 la-liga-2015-16 ligue-1-2015-16 serie-a-2015-16 champions-league-finals; do
  python train_xg_model.py --dataset $ds
  python build_pass_network.py --dataset $ds
  python score_players.py --dataset $ds
done
python build_datasets_index.py

# preview locally
cd ../site
python3 -m http.server 8000
# → open http://localhost:8000
```

## Deploying

Push this repo to GitHub, import it on [Vercel](https://vercel.com), and it just works — `vercel.json` points the output directory at `site/`, no build step needed since it's static files.

## Under the hood

- **xG model** — logistic regression on shot distance + angle to goal, trained on every non-penalty shot pooled across both datasets
- **Pass network** — average touch position per player, edges weighted by completed passes, capped to a club's busiest 16 players so the diagram stays legible
- **Value score** — xG per 90 minutes ÷ market value, normalized 0–100 within the dataset. Market values are a sample CSV (`data/market_values.csv`) you can swap for real figures

Full breakdown of every modeling choice and its limitations lives on the site's own methodology page — built to be read, not skipped.

## Stack

```
pipeline/   Python — pandas-free by design, just requests + scikit-learn + numpy
site/       Vanilla HTML/CSS/JS — Space Grotesk + Inter + JetBrains Mono, no framework
```

## Credit

Match data © [StatsBomb open data](https://github.com/statsbomb/open-data), used under their non-commercial license. Not affiliated with StatsBomb, UEFA, or the Premier League — this is a personal/portfolio project.

---

<div align="center">
<sub>Built as a portfolio project. If you use this as a starting point for your own, a ⭐ is always appreciated.</sub>
</div>
