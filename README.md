# LEIDSA Loto Mas Super Mas — Dashboard & Analysis

Exploratory data analysis, interactive dashboard, and (later) machine
learning models for LEIDSA's **Loto - Loto Mas - Super Mas** lottery draw
(Dominican Republic), covering the period since April 10, 2019.

This repo reads directly from Supabase (Postgres) — it does not scrape or
store its own copy of the data. The data pipeline that populates that
database lives in a separate repo:
[leidsa-supermas-pipeline](https://github.com/REPLACE_WITH_YOUR_USERNAME/leidsa-supermas-pipeline).

## Structure

```
notebooks/01_eda.ipynb   — exploratory data analysis
utils/data.py            — shared Supabase connection, queries, and CSV export
export_csv.py            — regenerates data/leidsa_supermas.csv from Supabase
data/leidsa_supermas.csv — committed CSV snapshot (wide format, 1 row per draw)
app.py                   — Streamlit dashboard (added in a later PR)
```

## Data source

Public, non-official lottery results aggregated from elboletoganador.com.
See the pipeline repo's README for details on collection and schema.

## Dual data source: Supabase or CSV

The notebook and dashboard can read from either source via `utils.data.load_data()`:

- `source="supabase"` — always reads live from Supabase (requires `SUPABASE_DB_URL` in `.env`)
- `source="csv"` — always reads from the committed `data/leidsa_supermas.csv` snapshot
- `source="auto"` (default used in the notebook) — tries Supabase first, falls back to the CSV snapshot if no connection is available

This means anyone cloning the repo can run the EDA notebook immediately
with the committed CSV, without needing Supabase credentials. After the
pipeline scrapes new draws, refresh the snapshot with:

```bash
python export_csv.py
```

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
