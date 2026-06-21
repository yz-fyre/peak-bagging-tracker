import streamlit as st
import pydeck as pdk

from dashboard.data import load_data

try:
    from src.pipeline import run_pipeline
except Exception:
    run_pipeline = None


def render_summary_metrics(df):
    total = len(df)
    completed = df["Completed"].sum()
    pct = round(completed / total * 100, 1) if total else 0
    total_height = df.loc[df["Completed"], "Height (Meters)"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Fells completed", f"{completed} / {total}")
    col2.metric("% complete", f"{pct}%")
    col3.metric("Total height climbed", f"{int(total_height):,} m")


def render_map(df):
    st.subheader("Map of fells")
    map_df = df.dropna(subset=["Latitude", "Longitude"]).copy()

    if map_df.empty:
        st.info("No fells with location data to show on the map.")
        return

    map_df["color"] = map_df["Completed"].apply(
        lambda c: [0, 150, 0] if c else [200, 30, 30]
    )
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
        tooltip={
            "html": "<b>{Name}</b><br/>Height: {Height (Meters)}m<br/>Completed: {Completed}"
        },
    ))
    st.caption("🟢 Completed   🔴 Not yet completed")


def render_ascents_per_year(df):
    st.subheader("Ascents per year")
    year_counts = (
        df[df["Completed"]]
        .groupby("Year Completed")
        .size()
        .reset_index(name="Ascents")
    )
    if year_counts.empty:
        st.info("No completed ascents yet for this group.")
        return
    st.bar_chart(year_counts.set_index("Year Completed"))


def render_full_table(df):
    st.subheader("All fells")
    st.dataframe(
        df[["Name", "Height (Meters)", "Completed", "Date Completed"]]
        .sort_values("Name")
    )


def render_overview_page(df):
    st.title("🏔️ Frank's Fell Walking Tracker")
    # Manual pipeline trigger
    if run_pipeline is None:
        st.info("Pipeline runner not available in this environment.")
    else:
        if st.button("Run pipeline now"):
            with st.spinner("Running full pipeline (extract → transform → load)…"):
                try:
                    run_pipeline()
                    st.success("Pipeline finished — refreshing the underlying data.")
                    df = load_data()
                except Exception as exc:  # noqa: BLE001 - surface runtime error to user
                    st.error(f"Pipeline failed: {exc}")
    render_summary_metrics(df)
    st.divider()
    render_map(df)
    st.divider()
    render_ascents_per_year(df)
    st.divider()
    render_full_table(df)


def render_group_page(df, group_name, flag_col):
    group_df = df[df[flag_col] == True].copy()  # noqa: E712

    st.title(f"🏔️ {group_name} Fells")

    if group_df.empty:
        st.info(f"No fells found for group '{group_name}'.")
        return

    render_summary_metrics(group_df)
    st.divider()
    render_map(group_df)
    st.divider()
    render_ascents_per_year(group_df)
    st.divider()
    render_full_table(group_df)