# LEIDSA Loto Mas Super Mas — Dashboard & Analysis

Exploratory data analysis, interactive dashboard, and (later) machine
learning models for LEIDSA's **Loto - Loto Mas - Super Mas** lottery draw
(Dominican Republic), covering the period since April 10, 2019.

This repo reads directly from Supabase (Postgres) — it does not scrape or
store its own copy of the data. The data pipeline that populates that
database lives in a separate repo:
[leidsa-supermas-pipeline](https://github.com/jorgedoiany/leidsa-supermas-pipeline.git).

## Structure

```
notebooks/01_eda.ipynb   — exploratory data analysis
utils/data.py            — shared Supabase connection and reusable queries
app.py                   — Streamlit dashboard (added in a later PR)
```

## Data source

Public, non-official lottery results aggregated from elboletoganador.com.
See the pipeline repo's README for details on collection and schema.

## Setup

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # fill in SUPABASE_DB_URL (use the Session pooler string)
```

## Usage

```bash
# EDA notebook
jupyter notebook notebooks/01_eda.ipynb

# Dashboard (once app.py is added)
streamlit run app.py
```

## Notes

- A lottery draw is a random process by design. This project is meant for
  descriptive, historical analysis — visualizing frequency, streaks, and
  distributions — not for predicting future draws.
