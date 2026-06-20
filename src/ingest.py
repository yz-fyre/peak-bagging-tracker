import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

from config import CREDENTIALS_FILE, SHEET_NAME

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_client():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return gspread.authorize(creds)


def load_sheet_as_dataframe(sheet_name: str = SHEET_NAME, worksheet_index: int = 1) -> pd.DataFrame:
    client = get_client()
    spreadsheet = client.open(sheet_name)
    worksheet = spreadsheet.get_worksheet(worksheet_index)
    records = worksheet.get_all_records()
    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    df = load_sheet_as_dataframe(worksheet_index=1)
    print(f"Loaded {len(df)} rows")
    print(df.head())