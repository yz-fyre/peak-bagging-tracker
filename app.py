import sys
sys.path.append("src")

import streamlit as st
import pandas as pd
import pydeck as pdk

from load import get_engine

st.set_page_config(page_title="Peak Bagging Dashboard", layout="wide")

@st.cache_data(ttl=300)
def load_data():
    """ Load the Fell data from Azure SQL Database into a Pandas DataFrame."""
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM wainwrights", engine)
    print(f"Loaded {len(df)} rows from Azure SQL Database")
    print(f"Columns: {df.columns.tolist()}")
    return df


df = load_data()

st.title("🏔️ Frank's Fell Walking Tracker")

# Summary metrics
total = len(df)
completed = df["Completed"].sum()
pct = round(completed / total * 100, 1)
total_height = df.loc[df["Completed"], "Height (Meters)"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Fells completed", f"{completed} / {total}")
col2.metric("% complete", f"{pct}%")
col3.metric("Total height climbed", f"{int(total_height):,} m")

st.divider()

# CompletionMap 
st.subheader("Map of fells")

map_df = df.dropna(subset=["Latitude", "Longitude"]).copy()
map_df["color"] = map_df["Completed"].apply(lambda c: [0, 150, 0] if c else [200, 30, 30])

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position=["Longitude", "Latitude"],
    get_fill_color="color",
    get_radius=300,
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=map_df["Latitude"].mean(),
    longitude=map_df["Longitude"].mean(),
    zoom=9,
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"html": "<b>{Name}</b><br/>Height: {Height (Meters)}m<br/>Completed: {Completed}"},
))

st.caption("🟢 Completed   🔴 Not yet completed")

st.divider()

# Ascents per year
st.subheader("Ascents per year")
year_counts = (
    df[df["Completed"]]
    .groupby("Year Completed")
    .size()
    .reset_index(name="Ascents")
)
st.bar_chart(year_counts.set_index("Year Completed"))

st.divider()

# Completion by area
st.subheader("Completion by area")
area_summary = (
    df.groupby("Area")["Completed"]
    .agg(["sum", "count"])
    .rename(columns={"sum": "Completed", "count": "Total"})
)
area_summary["% Complete"] = round(area_summary["Completed"] / area_summary["Total"] * 100, 1)
st.dataframe(area_summary)

st.divider()

# Full table 
st.subheader("All fells")
st.dataframe(
    df[["Name", "Area", "Height (Meters)", "Completed", "Date Completed"]]
    .sort_values("Name")
)