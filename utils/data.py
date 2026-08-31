"""
data.py
-------
Shared Supabase (Postgres) connection and reusable queries for the EDA
notebook and the Streamlit dashboard. Both consume the same functions here
so query logic lives in exactly one place.

Requires a SUPABASE_DB_URL environment variable (see .env.example).
Note: Supabase's direct connection host is IPv6-only unless the IPv4
add-on is purchased. Use the Session pooler connection string instead —
see the pipeline repo's README for details.
"""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

load_dotenv()


def get_engine() -> Engine:
    """Create a SQLAlchemy engine from SUPABASE_DB_URL."""
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        raise RuntimeError(
            "Missing SUPABASE_DB_URL. Define it in a .env file "
            "(see .env.example) or as an environment variable."
        )
    return create_engine(db_url)


def load_draws(engine: Engine | None = None) -> pd.DataFrame:
    """Load the draws table: 1 row per draw, with date, More/Super More numbers, etc."""
    engine = engine or get_engine()
    query = """
        SELECT draw_id, draw_number, draw_date, day_of_week,
               more_number, super_more_number, draw_time
        FROM draws
        ORDER BY draw_date
    """
    df = pd.read_sql(query, engine, parse_dates=["draw_date"])
    return df


def load_draw_numbers(engine: Engine | None = None) -> pd.DataFrame:
    """Load the draw_numbers table: 1 row per main drawn number (long format)."""
    engine = engine or get_engine()
    query = """
        SELECT draw_id, position, number
        FROM draw_numbers
        ORDER BY draw_id, position
    """
    return pd.read_sql(query, engine)


def load_merged(engine: Engine | None = None) -> pd.DataFrame:
    """
    Load draws joined with their 6 main numbers in long format — one row per
    (draw, number). This is the most convenient shape for frequency analysis
    (group by `number`) and for time-based charts (group by `draw_date`).
    """
    engine = engine or get_engine()
    query = """
        SELECT d.draw_id, d.draw_date, d.day_of_week,
               d.more_number, d.super_more_number,
               n.position, n.number
        FROM draws d
        JOIN draw_numbers n ON d.draw_id = n.draw_id
        ORDER BY d.draw_date, n.position
    """
    df = pd.read_sql(query, engine, parse_dates=["draw_date"])
    return df


def load_wide(engine: Engine | None = None) -> pd.DataFrame:
    """
    Load draws in wide format — one row per draw, with the 6 main numbers
    as separate columns (n1..n6) instead of long format. This is the shape
    used for the exported CSV snapshot and for human-readable inspection.
    """
    merged = load_merged(engine)
    wide = merged.pivot(
        index=["draw_id", "draw_date", "day_of_week", "more_number", "super_more_number"],
        columns="position",
        values="number",
    ).reset_index()
    wide.columns = [f"n{c}" if isinstance(c, int) else c for c in wide.columns]

    # Column order: identifiers, then the 6 main numbers, then the Mas /
    # Super Mas extras last (they are a separate part of the draw, not part
    # of the main 6-number combination).
    number_cols = [c for c in wide.columns if c.startswith("n") and c[1:].isdigit()]
    ordered_cols = ["draw_id", "draw_date", "day_of_week"] + number_cols + ["more_number", "super_more_number"]
    wide = wide[ordered_cols]

    wide = wide.sort_values("draw_date").reset_index(drop=True)
    return wide


def export_to_csv(path: str = "data/leidsa_supermas.csv", engine: Engine | None = None) -> pd.DataFrame:
    """
    Export a wide-format snapshot of the dataset to a local CSV. Run this
    manually (`python export_csv.py`) after the pipeline scrapes new draws,
    so the notebook stays reproducible for anyone cloning the repo without
    Supabase credentials.
    """
    wide = load_wide(engine)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    wide.to_csv(path, index=False)
    return wide


def load_data(source: str = "auto", csv_path: str = "data/leidsa_supermas.csv") -> pd.DataFrame:
    """
    Unified loader for the EDA notebook and dashboard, in wide format
    (1 row per draw, columns n1..n6 for the main numbers).

    source:
        "supabase" — always read live from Supabase.
        "csv"      — always read from the local CSV snapshot.
        "auto"     — try Supabase first; if the connection fails (e.g. no
                     SUPABASE_DB_URL set, as happens when someone else
                     clones the repo), fall back to the CSV snapshot.
    """
    if source == "csv":
        return pd.read_csv(csv_path, parse_dates=["draw_date"])
    if source == "supabase":
        return load_wide()

    try:
        return load_wide()
    except Exception as exc:
        print(f"Could not connect to Supabase ({exc}). Falling back to local CSV: {csv_path}")
        return pd.read_csv(csv_path, parse_dates=["draw_date"])

