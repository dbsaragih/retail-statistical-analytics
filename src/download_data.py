"""
download_data.py
Downloads the Online Retail II dataset from the UCI Machine Learning
Repository and saves it as a single Parquet file.

Source:  Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning
         Repository. https://doi.org/10.24432/C5CG6D
Licence: CC BY 4.0

Usage (from the project folder, with the retail-stats env active):
    python src/download_data.py
"""
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
ZIP_PATH = RAW_DIR / "online_retail_ii.zip"
PARQUET_PATH = RAW_DIR / "online_retail_ii.parquet"


def download():
    """Download the zip file once; skip if it already exists."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if ZIP_PATH.exists():
        print("Zip already downloaded, skipping.")
        return
    print("Downloading from UCI ...")
    urllib.request.urlretrieve(URL, ZIP_PATH)
    print(f"Saved {ZIP_PATH.name} ({ZIP_PATH.stat().st_size / 1e6:.1f} MB)")


def extract_excel():
    """Extract the zip (and any zip inside it) and return the Excel file path."""
    with zipfile.ZipFile(ZIP_PATH) as z:
        z.extractall(RAW_DIR)
    for inner in RAW_DIR.glob("*.zip"):
        if inner != ZIP_PATH:
            with zipfile.ZipFile(inner) as z:
                z.extractall(RAW_DIR)
    excel_files = list(RAW_DIR.glob("*.xlsx"))
    if not excel_files:
        raise FileNotFoundError("No .xlsx file found after extracting the zip.")
    return excel_files[0]


def convert_to_parquet(excel_path):
    """Read both yearly sheets, stack them, and save as Parquet."""
    print(f"Reading {excel_path.name} (this takes a few minutes) ...")
    sheets = pd.read_excel(
        excel_path,
        sheet_name=None,  # all sheets
        dtype={"Invoice": str, "StockCode": str, "Description": str},
    )
    df = pd.concat(sheets.values(), ignore_index=True)
    df.to_parquet(PARQUET_PATH, index=False)
    return df, list(sheets.keys())


def main():
    download()
    excel_path = extract_excel()
    df, sheet_names = convert_to_parquet(excel_path)
    print("\n--- Check ---")
    print("Sheets      :", sheet_names)
    print("Rows        :", f"{len(df):,}")
    print("Columns     :", list(df.columns))
    print("Date range  :", df["InvoiceDate"].min(), "to", df["InvoiceDate"].max())
    print("Saved       :", PARQUET_PATH)


if __name__ == "__main__":
    main()