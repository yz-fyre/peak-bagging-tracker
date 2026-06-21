import os

CREDENTIALS_FILE = os.getenv(
    "GOOGLE_BIG_QUERY_SA_CREDS", 
    "secrets/gbq-wainwirghts-bot-creds.json",
)
SHEET_NAME = "Peak Bagging"