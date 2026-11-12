"""
Publish the dashboard tables to Google Sheets, one tab per CSV, for Looker Studio.

Reads every CSV in reports/dashboard_data/ (except those in EXCLUDE) and writes it to a tab with the same name in
one Google Sheet, replacing the previous contents. A tab called `_about` records when and from where it was updated.

Setup (once): see docs/05_dashboard.md.
  - A Google Cloud service account with the Google Sheets API enabled
  - Its JSON key saved as .secrets/service_account.json (ignored by Git)
  - A Google Sheet shared with the service account's e-mail address (Editor)

Usage:
    python src/publish_to_sheets.py --sheet-id <ID>
    python src/publish_to_sheets.py                    # uses SHEET_ID from .secrets/sheet_id.txt
    python src/publish_to_sheets.py --dry-run          # list what would be published, no Google access
"""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "reports" / "dashboard_data"
SECRETS = ROOT / ".secrets"
KEY_FILE = SECRETS / "service_account.json"
SHEET_ID_FILE = SECRETS / "sheet_id.txt"

EXCLUDE = {"anomaly_invoice_scores.csv"}     # one score per invoice (39k rows): used for the R check, not the dashboard
MAX_CELLS = 10_000_000                       # Google Sheets limit per spreadsheet
PAUSE_SECONDS = 2.0                          # stay under the Sheets API limit of 60 write requests per minute


def load_tables():
    tables = {}
    for path in sorted(DASH.glob("*.csv")):
        if path.name in EXCLUDE:
            continue
        tables[path.stem] = pd.read_csv(path)
    return tables


def to_rows(df):
    """Header plus rows as plain Python values (JSON round trip turns NaN into empty cells)."""
    values = json.loads(df.to_json(orient="values", date_format="iso"))
    values = [["" if v is None else v for v in row] for row in values]
    return [list(map(str, df.columns))] + values


def publish(sheet_id, tables):
    import gspread                            # imported here so --dry-run works without it

    gc = gspread.service_account(filename=str(KEY_FILE))
    sh = gc.open_by_key(sheet_id)
    existing = {ws.title: ws for ws in sh.worksheets()}

    for name, df in tables.items():
        rows = to_rows(df)
        n_rows, n_cols = len(rows), max(len(rows[0]), 1)
        ws = existing.get(name) or sh.add_worksheet(title=name, rows=n_rows, cols=n_cols)
        ws.clear()
        ws.resize(rows=n_rows, cols=n_cols)
        ws.update(rows, "A1", value_input_option="USER_ENTERED")
        print(f"  {name:<34} {len(df):>6,} rows x {df.shape[1]:>2} columns")
        time.sleep(PAUSE_SECONDS)

    about = [["item", "value"],
             ["updated_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")],
             ["source", "reports/dashboard_data (retail-statistical-analytics)"],
             ["tables", len(tables)],
             ["data", "UCI Online Retail II, CC BY 4.0, https://doi.org/10.24432/C5CG6D"]]
    ws = existing.get("_about") or sh.add_worksheet(title="_about", rows=len(about), cols=2)
    ws.clear()
    ws.update(about, "A1", value_input_option="RAW")

    default = existing.get("Sheet1") or existing.get("Sheet 1")
    if default is not None and len(sh.worksheets()) > 1:
        sh.del_worksheet(default)             # remove the empty starter tab
    print(f"\nDone: {len(tables)} tables published to https://docs.google.com/spreadsheets/d/{sheet_id}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sheet-id", help="ID of the Google Sheet (the long code in its URL)")
    parser.add_argument("--dry-run", action="store_true", help="list the tables without publishing")
    args = parser.parse_args()

    tables = load_tables()
    cells = sum((len(df) + 1) * df.shape[1] for df in tables.values())
    print(f"Tables in {DASH.relative_to(ROOT)}: {len(tables)}   cells: {cells:,} (limit {MAX_CELLS:,})")
    if cells > MAX_CELLS:
        raise SystemExit("Too many cells for one Google Sheet; add large tables to EXCLUDE.")

    if args.dry_run:
        for name, df in tables.items():
            print(f"  {name:<34} {len(df):>6,} rows x {df.shape[1]:>2} columns")
        return

    sheet_id = args.sheet_id or (SHEET_ID_FILE.read_text().strip() if SHEET_ID_FILE.exists() else None)
    if not sheet_id:
        raise SystemExit("No sheet ID: pass --sheet-id or save it in .secrets/sheet_id.txt")
    if not KEY_FILE.exists():
        raise SystemExit(f"Service account key not found: {KEY_FILE}")
    publish(sheet_id, tables)


if __name__ == "__main__":
    main()
