"""
Combined pipeline: pulls data from Google Sheets, cleans/transforms it,
and loads it into Azure SQL Database.

Run manually whenever you've updated your Wainwrights Google Sheet:
    python src/main.py
"""

import pandas as pd
from extract import load_sheet_as_dataframe
from transform import transform, compute_metrics
from load import load_dataframe


def run_pipeline():
    print("Step 1/3: Extracting data from Google Sheets...")
    raw_df = load_sheet_as_dataframe()
    print(f"  Loaded {len(raw_df)} rows")

    print("Step 2/3: Transforming and cleaning data...")
    clean_df = transform(raw_df)
    metrics = compute_metrics(clean_df)
    print(f"Completed {metrics['completed']} / {metrics['total_fells']} ({metrics['pct_complete']}%)")
    print(f"Total height climbed: {metrics['total_height_climbed_m']} m")
    print(f"\nWainwrights Completed: {metrics['completed_wainwrights']} ({metrics['pct_completed_wainwrights']}%)")
    print(f"Outerlying Fells Completed: {metrics['completed_outerlying_fells']} ({metrics['pct_completed_outerlying_fells']}%)")
    print(f"Birkett Fells Completed: {metrics['completed_birkett_fells']} ({metrics['pct_completed_birkett_fells']}%)")
    print(f"Dales 30 Fells Completed: {metrics['completed_dales_30_fells']} ({metrics['pct_completed_dales_30_fells']}%)")

    print("Step 3/3: Loading into Azure SQL...")
    load_dataframe(clean_df, "wainwrights")

    print("\nPipeline complete! Refresh your Dashboard to see the latest data.")


if __name__ == "__main__":
    run_pipeline()