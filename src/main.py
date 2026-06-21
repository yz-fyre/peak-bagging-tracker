"""
Combined pipeline: pulls data from Google Sheets, cleans/transforms it,
and loads it into Azure SQL Database.

Run manually whenever you've updated your Wainwrights Google Sheet:
    python src/main.py
"""

from ingest import load_sheet_as_dataframe
from transform import clean_data, compute_metrics
from load import load_dataframe


def run_pipeline():
    print("Step 1/3: Pulling data from Google Sheets...")
    raw_df = load_sheet_as_dataframe()
    print(f"  Loaded {len(raw_df)} rows")

    print("Step 2/3: Cleaning and transforming...")
    clean_df = clean_data(raw_df)
    metrics = compute_metrics(clean_df)
    print(f"  Completed {metrics['completed']} / {metrics['total_fells']} "
          f"({metrics['pct_complete']}%)")
    print(f"  Total height climbed: {metrics['total_height_climbed_m']} m")

    print("Step 3/3: Loading into Azure SQL...")
    load_dataframe(clean_df, "wainwrights")

    print("\nPipeline complete! Refresh your Power BI dataset to see the latest data.")


if __name__ == "__main__":
    run_pipeline()