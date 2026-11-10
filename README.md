# 🏅 Olympics Analytics

An interactive Streamlit app exploring **120 years of Summer Olympics data** (1896–2016), with two
machine-learning tools: a **sport recommender** and a **medal-count forecaster**.

> Data: [120 years of Olympic history](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results) (`athlete_events.csv`, `noc_regions.csv`).

## Features

| Page | What it does |
|---|---|
| Home | Headline stats, record holders, all-time top-10 chart |
| Medal Tally | Filter by edition and country, stacked medal charts, CSV download |
| Overall Analysis | Growth of nations/events/athletes, events-per-sport heatmap, top athletes by sport |
| Country Analysis | Per-country KPIs, medals over time, sport heatmap, top athletes |
| Athlete Analysis | Age distributions, age by sport, height vs weight, men vs women |
| **World Map** | Choropleth of medals, with an animation through every edition |
| **Country vs Country** | Head-to-head medals, per-edition wins, strongest sports |
| **Host Advantage** | Host share of medals vs. usual share, with caveats |
| **Sport Matcher (ML)** | Random forest: sex/age/height/weight → top-5 sports (top-k accuracy shown) |
| **Medal Predictor (ML)** | Gradient boosting back-tested on 2008–2016, forecast for the next edition |

## Run it

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

Tests: `pip install -r requirements-dev.txt && pytest`

Deploy: push to GitHub, then create the app on Streamlit Community Cloud with **main file `Home.py`**.
(`athlete_events.csv` is ~40 MB, which is fine for GitHub; if you prefer, convert it to Parquet.)

## Project structure

```
Home.py                  landing page
pages/                   one file per page (Streamlit multipage)
utils/constants.py       hosts, colours, NOC→ISO map
utils/data.py            loading + preprocessing (cached)
utils/analysis.py        pure pandas functions (unit-tested)
utils/models.py          sport matcher + medal forecaster
utils/ui.py              theme, CSS, chart helpers
tests/                   pytest suite
data/                    the two CSVs
```

## Methodology notes

- **Team medals count once.** Medals are de-duplicated per `(Team, Games, Event, Medal)`, so a football gold is one medal, not 11.
- **Summer Games only.** The Intercalated 1906 Games are shown in the data but excluded from the "Editions" count and from the ML panel.
- **Men vs women** counts each athlete once *per edition* (the original counted an athlete once across their whole career, which under-counts).
- **Historical teams** (USSR, East/West Germany, Yugoslavia…) map to the modern country in the `region` column.

### Sport Matcher
Trained on medalists in the 20 sports with the most medalists (80/20 stratified split). Reports top-1 and top-3
accuracy against a "always guess the most common sport" baseline. Body measurements are a weak signal, so it's framed as a fun profile match.

### Medal Predictor
Panel of country × edition. Features: last edition's medals, two editions ago, rolling 3-edition mean, athletes sent,
experience, host flag. Back-test: train before 2008, predict 2008/2012/2016. It beats a "same as last time" baseline
modestly overall, and more clearly for host nations and medal contenders. Limitations are listed in the app.

## Ideas for next steps
- Add Tokyo 2020 / Paris 2024 data and compare against the forecast
- Add GDP and population for per-capita medals and better forecasts
- Prediction intervals, SHAP explanations
- Winter Games toggle
