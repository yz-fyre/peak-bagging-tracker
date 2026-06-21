import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

load_dotenv(dotenv_path="secrets/.env")

SERVER = os.getenv("AZURE_SQL_SERVER")
DATABASE = os.getenv("AZURE_SQL_DATABASE")
USERNAME = os.getenv("AZURE_SQL_USERNAME")
PASSWORD = os.getenv("AZURE_SQL_PASSWORD")

CONNECTION_STRING = (
    f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}:1433/{DATABASE}"
    "?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no&timeout=60"
)


def get_engine():
    """ Create a SQLAlchemy engine for the Azure SQL Database. """
    return create_engine(CONNECTION_STRING)


def load_dataframe(df: pd.DataFrame, table_name: str = "wainwrights"):
    """ Load a pandas DataFrame into the specified SQL table. """
    engine = get_engine()
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into table '{table_name}'")


if __name__ == "__main__":
    from ingest import load_sheet_as_dataframe
    from transform import clean_data

    raw_df = load_sheet_as_dataframe()
    clean_df = clean_data(raw_df)
    load_dataframe(clean_df, "wainwrights")