"""
export_csv.py
--------------
Regenerates the local CSV snapshot of the dataset (data/leidsa_supermas.csv)
by pulling the current data from Supabase. Run this after the pipeline
scrapes new draws, so the notebook and repo stay reproducible for anyone
cloning it without Supabase credentials.

Usage:
    python export_csv.py
"""

from utils.data import export_to_csv

if __name__ == "__main__":
    df = export_to_csv()
    print(f"Exported {len(df)} rows to data/leidsa_supermas.csv")
    print(f"Date range: {df['draw_date'].min().date()} -> {df['draw_date'].max().date()}")
