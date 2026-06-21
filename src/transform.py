import pandas as pd
from OSGridConverter import grid2latlong


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """ Clean and normalise the raw data from the Google Sheet. """
    df = df.copy()

    # Normalise column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Boolean: completed or not
    df["Completed"] = df["Completed (Y/N)"].str.strip().str.upper() == "Y"

    # Parse date (blank stays NaT for incomplete fells)
    df["Date Completed"] = pd.to_datetime(df["Date Completed"], format="%m/%d/%Y", errors="coerce")

    # Make sure height is numeric
    df["Height (Meters)"] = pd.to_numeric(df["Height (Meters)"], errors="coerce")
    df["Height (Feet)"] = pd.to_numeric(df["Height (Feet)"], errors="coerce")

    # Rename
    df["Area"] = df["Wainy Book Ref"]

    # Year completed, for ascents-per-year metric
    df["Year Completed"] = df["Date Completed"].dt.year

    # Month completed
    df["Month Completed"] = df["Date Completed"].dt.month

    return df


def compute_metrics(df: pd.DataFrame) -> dict:
    """ Compute summary metrics from the cleaned data. """
    total_fells = len(df)
    completed = df["Completed"].sum()
    pct_complete = round((completed / total_fells) * 100, 1)

    total_height_climbed = df.loc[df["Completed"], "Height (Meters)"].sum()

    ascents_per_year = (
        df.loc[df["Completed"], "Year Completed"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    ascents_per_month = (
        df.loc[df["Completed"], "Month Completed"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    completion_by_area = (
        df.groupby("Area")["Completed"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "completed", "count": "total"})
    )
    completion_by_area["pct_complete"] = round(
        completion_by_area["completed"] / completion_by_area["total"] * 100, 1
    )

    return {
        "total_fells": total_fells,
        "completed": int(completed),
        "pct_complete": pct_complete,
        "total_height_climbed_m": float(total_height_climbed),
        "ascents_per_year": ascents_per_year,
        "ascents_per_month": ascents_per_month,
        "completion_by_area": completion_by_area,
    }


def grid_ref_to_lat_lon(grid_ref: str):
    """
    Convert a single OS Grid Reference string (e.g. "NY266307") into
    a (latitude, longitude) tuple. Returns (None, None) if conversion fails
    (e.g. blank or malformed grid ref).
    """
    if not grid_ref or not isinstance(grid_ref, str):
        return None, None

    grid_ref = grid_ref.strip().replace(" ", "")
    if len(grid_ref) < 6:
        return None, None

    try:
        location = grid2latlong(grid_ref)
        return location.latitude, location.longitude
    except Exception:
        return None, None


if __name__ == "__main__":
    from ingest import load_sheet_as_dataframe  

    raw_df = load_sheet_as_dataframe()
    clean_df = clean_data(raw_df)
    clean_df[["Latitude", "Longitude"]] = clean_df["OS Grid Ref"].apply(lambda gr: pd.Series(grid_ref_to_lat_lon(gr)))
    metrics = compute_metrics(clean_df)

    print("New dataset columns:")
    print(clean_df.columns.tolist())
    print("Example of Cleaned dataset data:")
    print(clean_df.head())
    print(f"Completed {metrics['completed']} / {metrics['total_fells']} ({metrics['pct_complete']}%)")
    print(f"Total height climbed: {metrics['total_height_climbed_m']} m")
    print("\nAscents per year:")
    print(metrics["ascents_per_year"])
    print("\nAscents per month:")
    print(metrics["ascents_per_month"])
    print("\nCompletion by area:")
    print(metrics["completion_by_area"])