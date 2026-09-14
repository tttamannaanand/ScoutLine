"""
Defines the club datasets this project pulls from StatsBomb's open data.

Each dataset is one or more (competition_id, season_id) pairs to fetch and
pool together. StatsBomb's free open data only ships the FINAL of each
Champions League season (not a full season of matches) — so the CL dataset
here is a "finals archive" across many years, pooling different clubs
together, rather than one full competition season the way the Premier
League dataset is. See README.md for the full explanation.
"""

# Full 2015/16 Premier League season: all 380 matches, all 20 clubs.
PREMIER_LEAGUE_2015_16 = {
    "id": "premier-league-2015-16",
    "label": "Premier League 2015/16",
    "short_label": "PL 15/16",
    "competitions": [(2, 27)],
}

# Every Champions League final StatsBomb has released as open data,
# 1970/71 through 2018/19 - 18 matches, spanning many different clubs
# across different eras rather than one season.
CHAMPIONS_LEAGUE_FINALS = {
    "id": "champions-league-finals",
    "label": "Champions League finals, 1970-2019",
    "short_label": "UCL finals",
    "competitions": [
        (16, 276), (16, 71), (16, 277), (16, 76), (16, 44), (16, 37),
        (16, 39), (16, 41), (16, 21), (16, 22), (16, 23), (16, 24),
        (16, 25), (16, 26), (16, 27), (16, 2), (16, 1), (16, 4),
    ],
}

# Full 2015/16 La Liga season: all 380 matches, all 20 clubs.
LA_LIGA_2015_16 = {
    "id": "la-liga-2015-16",
    "label": "La Liga 2015/16",
    "short_label": "La Liga 15/16",
    "competitions": [(11, 27)],
}

# Full 2015/16 Ligue 1 season: 377 of 380 matches released, all 20 clubs.
LIGUE_1_2015_16 = {
    "id": "ligue-1-2015-16",
    "label": "Ligue 1 2015/16",
    "short_label": "Ligue 1 15/16",
    "competitions": [(7, 27)],
}

# Full 2015/16 Serie A season: all 380 matches, all 20 clubs.
SERIE_A_2015_16 = {
    "id": "serie-a-2015-16",
    "label": "Serie A 2015/16",
    "short_label": "Serie A 15/16",
    "competitions": [(12, 27)],
}

DATASETS = [
    PREMIER_LEAGUE_2015_16,
    LA_LIGA_2015_16,
    LIGUE_1_2015_16,
    SERIE_A_2015_16,
    CHAMPIONS_LEAGUE_FINALS,
]
DATASET_BY_ID = {d["id"]: d for d in DATASETS}
