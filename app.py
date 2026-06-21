import sys
sys.path.append("src")

import streamlit as st

# Custom modules
from dashboard.data import load_data, get_flag_groups
from dashboard.views import render_overview_page, render_group_page

st.set_page_config(page_title="Peak Bagging Dashboard", layout="wide")

df = load_data()
groups = get_flag_groups(df)


def make_group_page(group_name, flag_col):
    # Default-arg trick avoids late-binding closure bugs in the loop below
    def _page(group_name=group_name, flag_col=flag_col):
        render_group_page(df, group_name, flag_col)
    return _page

pages = [
    st.Page(lambda: render_overview_page(df), title="Overview", icon="🏔️", url_path="overview"),
]
 
for group_name, flag_col in groups:
    pages.append(
        st.Page(
            make_group_page(group_name, flag_col),
            title=group_name + " Fells",
            url_path=group_name.lower().replace(" ", "-"),
        )
    )
 
pg = st.navigation(pages)
pg.run()