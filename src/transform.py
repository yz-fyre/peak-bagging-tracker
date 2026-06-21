import pandas as pd
from OSGridConverter import grid2latlong

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """ Transform the raw data from the Google Sheet into a cleaned and enriched DataFrame using functions defined below. """
    df = clean_data(df)
    df = add_completion_date_parts(df)
    df[["Latitude", "Longitude"]] = df["OS Grid Ref"].apply(lambda gr: pd.Series(grid_ref_to_lat_lon(gr)))
    
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """ Clean and normalise the raw data from the Google Sheet. """
    df = df.copy()

    # Normalise column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Boolean: completed or not
    df["Completed"] = df["Completed (Y/N)"].str.strip().str.upper() == "Y"

    # Boolean: X Group or not
    df["Wainwright Flag"] = df["Wainwright_indicator"].str.strip().str.upper() == "Y"
    df["Birkett Flag"] = df["Birkett_indicator"].str.strip().str.upper() == "Y"
    df["Outerlying Flag"] = df["Outerlying_indicator"].str.strip().str.upper() == "Y"
    df["Dales 30 Flag"] = df["Dales_30_indicator"].str.strip().str.upper() == "Y"

    # Make sure height is numeric
    df["Height (Meters)"] = pd.to_numeric(df["Height (Meters)"], errors="coerce")
    df["Height (Feet)"] = pd.to_numeric(df["Height (Feet)"], errors="coerce")

    return df

def add_completion_date_parts(df: pd.DataFrame, date_column: str = "Date Completed") -> pd.DataFrame:
    """Parse completion dates and add date-derived columns."""
    df[date_column] = pd.to_datetime(df[date_column], format="%m/%d/%Y", errors="coerce")
    df["Year Completed"] = df[date_column].dt.year
    df["Quarter Completed"] = df[date_column].dt.quarter
    df["Month Completed"] = df[date_column].dt.month
    return df

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

def compute_metrics(df: pd.DataFrame) -> dict:
    """ Compute summary metrics from the cleaned data. """
    total_fells = len(df)
    completed = df["Completed"].sum()
    pct_complete = round((completed / total_fells) * 100, 1)

    total_height_climbed = df.loc[df["Completed"], "Height (Meters)"].sum()

    # Number of completed Wainwrights
    wainwrights_completed = int(
        df.loc[(df["Wainwright Flag"] == True) & (df["Completed"]),].shape[0]
    )

    # Number of completed Outerlying Fells
    outerlying_fells_completed = int(
        df.loc[(df["Outerlying Flag"] == True) & (df["Completed"]),].shape[0]
    )

    # Number of completed Birkett Fells
    birkett_fells_completed = int(
        df.loc[(df["Birkett Flag"] == True) & (df["Completed"]),].shape[0]
    )

    # Number of completed Dale 30 Fells
    dales_30_fells_completed = int(
        df.loc[(df["Dales 30 Flag"] == True) & (df["Completed"]),].shape[0]
    )

    # Totals for each category (to compute percentages)
    total_wainwrights = int(df["Wainwright Flag"].sum())
    total_outerlying = int(df["Outerlying Flag"].sum())
    total_birkett = int(df["Birkett Flag"].sum())
    total_dales_30 = int(df["Dales 30 Flag"].sum())

    # Percentages (guard division by zero)
    pct_completed_wainwrights = (
        round(wainwrights_completed / total_wainwrights * 100, 1) if total_wainwrights else 0.0
    )
    pct_completed_outerlying = (
        round(outerlying_fells_completed / total_outerlying * 100, 1) if total_outerlying else 0.0
    )
    pct_completed_birkett = (
        round(birkett_fells_completed / total_birkett * 100, 1) if total_birkett else 0.0
    )
    pct_completed_dales_30 = (
        round(dales_30_fells_completed / total_dales_30 * 100, 1) if total_dales_30 else 0.0
    )

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

    return {
        "total_fells": total_fells,
        "completed": int(completed),
        "pct_complete": pct_complete,
        "total_height_climbed_m": float(total_height_climbed),
        "ascents_per_year": ascents_per_year,
        "ascents_per_month": ascents_per_month,
        "completed_wainwrights": wainwrights_completed,
        "completed_outerlying_fells": outerlying_fells_completed,
        "completed_birkett_fells": birkett_fells_completed,
        "completed_dales_30_fells": dales_30_fells_completed,
        "pct_completed_wainwrights": pct_completed_wainwrights,
        "pct_completed_outerlying_fells": pct_completed_outerlying,
        "pct_completed_birkett_fells": pct_completed_birkett,
        "pct_completed_dales_30_fells": pct_completed_dales_30,
    }


""" can be run as a standalone script to test the transformation and metrics computation """
if __name__ == "__main__":
    from extract import load_sheet_as_dataframe  

    print("Loading raw data from Google Sheet...")
    raw_df = load_sheet_as_dataframe()
    print(f"Loaded {len(raw_df)} rows from Google Sheet")
    print("Transforming data...")
    transformed_df = transform(raw_df)
    print("Computing metrics...")
    metrics = compute_metrics(transformed_df)

    print("New dataset columns:")
    print(transformed_df.columns.tolist())
    print("Example of Transformed dataset data:")
    print(transformed_df.head())

    print(f"Completed {metrics['completed']} / {metrics['total_fells']} ({metrics['pct_complete']}%)")
    print(f"Total height climbed: {metrics['total_height_climbed_m']} m")
    
    print("\nAscents per year:")
    print(metrics["ascents_per_year"])
    
    print("\nAscents per month:")
    print(metrics["ascents_per_month"])

    print(f"\nWainwrights Completed: {metrics['completed_wainwrights']} ({metrics['pct_completed_wainwrights']}%)")
    print(f"Outerlying Fells Completed: {metrics['completed_outerlying_fells']} ({metrics['pct_completed_outerlying_fells']}%)")
    print(f"Birkett Fells Completed: {metrics['completed_birkett_fells']} ({metrics['pct_completed_birkett_fells']}%)")
    print(f"Dales 30 Fells Completed: {metrics['completed_dales_30_fells']} ({metrics['pct_completed_dales_30_fells']}%)")