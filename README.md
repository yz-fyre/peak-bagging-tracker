# Peak Bagging Dashboard

Personal Project to ingest my "Peak Bagging" Google sheet and visualise the data. Goal is to learn more about Azure and PowerBI  Built primarily as a hands-on learning vehicle for data engineering skills (extraction, transformation, loading, cloud infrastructure), with the added bonus of a genuinely useful personal tracker. Built with support from Generative AI.

## What it does

1. **Extract** — Pulls raw walk-tracking data from a personal Google Sheet via the Google Sheets API.
2. **Transform** — Cleans the data with pandas and computes summary metrics: completion percentage, total height climbed, ascents per year, and completion breakdown by area.
3. **Load** — Writes the cleaned data into an Azure SQL Database.

The pipeline is run manually (`python src/main.py`) whenever the source sheet is updated — automation is a deliberate "later" step, see Roadmap below.

## Architecture

```bash
Google Sheet  →  Python (ingest + transform)  →  Azure SQL Database  →  BI dashboard
```

- **Source**: Google Sheets, accessed via a Google Cloud service account
- **Processing**: Python (pandas, gspread, google-auth)
- **Storage**: Azure SQL Database (serverless, free tier)
- **Visualisation**: TBD — see Roadmap

## Project structure

```bash
wainwrights-dashboard/
├── secrets/
│   ├──.env                             # Azure SQL credentials (gitignored)
│   └──gbq-wainwrights-bot-creds.json   # Google Big Query Service Account credentials (gitignored)
├── .gitignore
├── requirements.txt
├── src/
│   ├── config.py         # Credentials file path, sheet name
│   ├── ingest.py         # Pulls Google Sheet data into a DataFrame
│   ├── transform.py      # Cleans data, computes metrics
│   ├── load.py           # Writes data to Azure SQL
│   └── main.py           # Runs the full pipeline end to end
├── azure-sql-queries/
│   └── simple-queries.sql  # Storage for queries as not persisted on Azure
└── README.md
```

## Source data

The Google Sheet tracks each fell with the following columns:

| Column | Description |
|---|---|
| Name | Fell name |
| Wainy / Birkett / Outerlying Fell | Classification flags |
| Wainy Book Ref | Which of Wainwright's seven guidebooks the fell belongs to (used to derive Area) |
| Birkett Group Ref | Alternative grouping reference |
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
   python src/main.py
```

## Roadmap

- [ ] **BI dashboard** — connect a BI tool to the Azure SQL Database to visualise progress (completion %, ascents over time, area breakdown, summit map). Tool choice still open — leading candidates are Power BI and Streamlit, decision pending hands-on evaluation.
- [ ] **Pipeline automation** — currently run manually after each sheet update. Likely candidate: an **Azure Function on a timer trigger**, since the pipeline is already in Python and this keeps everything within the same cloud ecosystem and free tier. (GitHub Actions on a schedule is a simpler alternative worth considering if Azure Functions adds too much complexity for the benefit.)
- [ ] Add a map visual using OS Grid References converted to latitude/longitude
- [ ] Add data validation/tests around the transform step
- [ ] Track historical snapshots rather than overwriting the table on each load, to enable a "progress over time" view