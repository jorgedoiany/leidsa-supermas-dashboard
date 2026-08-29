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


def number_frequency(engine: Engine | None = None) -> pd.DataFrame:
    """
    Frequency of each of the 6 main numbers (1-40) across all draws.
    Returns a DataFrame with columns: number, times_drawn.
    """
    df = load_draw_numbers(engine)
    freq = (
        df["number"]
        .value_counts()
        .rename_axis("number")
        .reset_index(name="times_drawn")
        .sort_values("number")
        .reset_index(drop=True)
    )
    return freq
