# Peak Bagging Dashboard

Personal project to ingest my "Peak Bagging" Google Sheet of fell climbs, transform the data, and load it into Azure SQL for downstream reporting.

## What it does

1. **Extract** — Pulls raw walk-tracking data from a personal Google Sheet via the Google Sheets API.
2. **Transform** — Cleans the data with pandas and computes summary metrics: completion percentage, total height climbed, ascents per year, and completion breakdown by area.
3. **Load** — Writes the cleaned data into an Azure SQL Database.

The pipeline can be run locally(`python src/pipeline.py`) or automated via GitHub Actions (scheduled runs or on push to `main`).

## Architecture

```bash
Google Sheet  →  Python (ingest + transform)  →  Azure SQL Database  →  Streamlit dashboard
```

- **Source**: Google Sheets, accessed via a Google Cloud service account
- **Processing**: Python (pandas, gspread, google-auth)
- **Storage**: Azure SQL Database (serverless, free tier)
- **Visualisation**: TBD — see Roadmap

## Project structure

```bash
peak-bagging-tracker/
├── .github/workflows
│   └──pipeline.yml                   # Azure SQL credentials (gitignored)
│
├── secrets/
│   ├──.env                             # Azure SQL credentials (gitignored)
│   └──gbq-wainwrights-bot-creds.json   # Google Big Query Service Account credentials (gitignored)
│
├── src/
│   ├── config.py         # Credentials file path, sheet name
│   ├── extract.py        # Pulls Google Sheet data into a DataFrame
│   ├── transform.py      # Cleans data, computes metrics
│   ├── load.py           # Writes data to Azure SQL
│   └── pipeline.py       # Runs the full ETL pipeline end to end
│
├── azure-sql-queries/
│   └── simple-queries.sql  # Storage for queries as not persisted on Azure
│
├── README.md
├── .gitignore
└── requirements.txt
```

## Source data

The Google Sheet tracks each fell with the following columns:

| Column | Description |
|---|---|
| Name | Fell name |
| Wainy / Birkett / Outerlying Fell / Dales 30| Classification flags |
| Wainy Book Ref | Which of Wainwright's seven guidebooks the fell belongs (or.. The Outerlying Fells) |
| Birkett Group Ref | Grouping reference for Bill Birkets Fells |
| Dales 30 Ref | Grouping Reference for Dales 30 |
| Height (Feet) / Height (Meters) | Fell height |
| OS Grid Ref | Grid reference for the summit |
| Completed (Y/N) | Whether the fell has been climbed |
| Date Completed | Date of ascent |

## Setup

1. Clone the repo and create a virtual environment:
```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```
2. Set up a Google Cloud service account with Sheets API access, share your sheet with it, and save the credentials JSON (filename referenced in `src/config.py`).
3. Create an Azure SQL Database (free tier used for this dataset size) and add the connection details to a `.env` file:
```bash    
    AZURE_SQL_SERVER=your-server.database.windows.net
    AZURE_SQL_DATABASE=your-database
    AZURE_SQL_USERNAME=your-username
    AZURE_SQL_PASSWORD=your-password
```

4. Run the pipeline:
```bash
   python src/pipeline.py
```

## Automation

You can automate runs of the ETL pipeline using GitHub Actions (recommended) or a cloud scheduler (Azure Function, App Service cron, etc.). The recommended pattern is a scheduled GitHub Actions workflow that runs `python src/pipeline.py` on a cron schedule and/or on push to `main`.

Required repository secrets (store in GitHub Settings → Secrets):

- `GOOGLE_BIG_QUERY_SA_CREDS` — base64-encoded Google service account JSON or the JSON itself (used by `gspread`/Google client)
- `AZURE_SQL_SERVER`, `AZURE_SQL_DATABASE`, `AZURE_SQL_USERNAME`, `AZURE_SQL_PASSWORD` — database connection details

Notes:

- If you store the service account JSON as a secret, write it to `secrets/` at runtime as shown above.
- Consider adding simple logging and error notifications (email or Slack) in the workflow for failure alerts.
- Alternatively, deploy an Azure Function with a timer trigger if you prefer running inside Azure.


## Roadmap

- [ ] **BI dashboard** — connect a BI tool to the Azure SQL Database to visualise progress (completion %, ascents over time, area breakdown, summit map). Tool choice still open — leading candidates are Power BI and Streamlit, decision pending hands-on evaluation.
- [X] **Pipeline automation** — currently run manually after each sheet update. Likely candidate: an **Azure Function on a timer trigger**, since the pipeline is already in Python and this keeps everything within the same cloud ecosystem and free tier. (GitHub Actions on a schedule is a simpler alternative worth considering if Azure Functions adds too much complexity for the benefit.)
- [ ] Add a map visual using OS Grid References converted to latitude/longitude
- [ ] Add data validation/tests around the transform step
- [ ] Track historical snapshots rather than overwriting the table on each load, to enable a "progress over time" view