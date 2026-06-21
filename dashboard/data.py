import sys
sys.path.append("src")
 
import time
import streamlit as st
import pandas as pd
 
from load import get_engine

@st.cache_data(ttl=300)
def load_data():
    """ Load the Fell data from Azure SQL Database into a Pandas DataFrame."""
    max_attempts = 4
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            with st.spinner(f"Waking up the database, This can take up to a minute (attempt {attempt}/{max_attempts})..."):
                engine = get_engine()
                df = pd.read_sql("SELECT * FROM wainwrights", engine)
            return df
        except Exception as e:
            last_error = e
            if attempt < max_attempts:
                time.sleep(10)

    st.error(
        f"Could not connect to the database after {max_attempts} attempts. "
        f"The database may be unavailable. Error: {last_error}"
    )
    st.stop()

def get_flag_groups(df):
    """Discover fell groups dynamically from columns ending in ' Flag'.
 
    Returns a list of (group_name, flag_column) tuples, e.g.
    [("Wainwright", "Wainwright Flag"), ("Birkett", "Birkett Flag"), ...]
    """
    flag_cols = [c for c in df.columns if c.endswith(" Flag")]
    return [(c.removesuffix(" Flag"), c) for c in flag_cols]