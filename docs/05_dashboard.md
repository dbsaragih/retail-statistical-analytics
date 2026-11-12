# 05 Dashboard: Google Sheets → Looker Studio

The notebooks write summary tables to `reports/dashboard_data/` (one CSV per table). `src/publish_to_sheets.py`
copies them into one Google Sheet, one tab per table, and Looker Studio reads that Sheet. Re-running the notebooks and
the script refreshes the dashboard; the Looker Studio report itself does not need to change.

```
notebooks (Python) ──► reports/dashboard_data/*.csv ──► publish_to_sheets.py ──► Google Sheet ──► Looker Studio
```

## One-time setup

### 1. Google Cloud service account

1. Go to <https://console.cloud.google.com/> and create a project, e.g. `retail-dashboard`.
2. **APIs & Services → Library**: enable **Google Sheets API** and **Google Drive API**.
3. **APIs & Services → Credentials → Create credentials → Service account**: name it e.g. `sheets-publisher`; no roles are needed.
4. Open the service account → **Keys → Add key → Create new key → JSON**. A `.json` file downloads.
5. Save it in the project as `.secrets/service_account.json`. The `.secrets/` folder is in `.gitignore`: the key must never be committed.
6. Note the service account's e-mail address (`...@<project>.iam.gserviceaccount.com`).

### 2. The Google Sheet

1. Create an empty Google Sheet, e.g. **Retail Statistical Analytics – dashboard data**.
2. **Share** it with the service account e-mail as **Editor**.
3. Copy the Sheet ID: the long code between `/d/` and `/edit` in its URL. Save it in `.secrets/sheet_id.txt`.

### 3. Python package (WSL environment)

```bash
~/venvs/stats/bin/pip install gspread
```

## Publishing

```bash
~/venvs/stats/bin/python src/publish_to_sheets.py --dry-run     # list the tables, no Google access
~/venvs/stats/bin/python src/publish_to_sheets.py               # publish
```

Each run replaces the contents of every tab and updates the `_about` tab with the time of publication.
`anomaly_invoice_scores.csv` (one score per invoice) is excluded: it is used for the Python–R check, not the dashboard.

## Report design

Each tab becomes a Looker Studio data source (**Add data → Google Sheets → the Sheet → tab**, with "Use first row as
headers" ticked). Pages and the tables behind them:

| Page | Purpose | Charts | Tables (tabs) |
|---|---|---|---|
| 1. Overview | How is the business doing? | Scorecards (net revenue, orders, value per order, customers); monthly net revenue, Year 1 vs Year 2; weekly revenue | `monthly_kpis`, `weekly_revenue` |
| 2. Seasonality | When do customers buy? | Revenue by weekday and by hour | `weekday_pattern`, `hour_pattern` |
| 3. Customers | Who are the customers? | RFM segments: share of customers vs revenue; cluster profiles; filterable customer table | `customer_rfm_segments`, `customer_clusters`, `customer_rfm` |
| 4. Products | What sells, and together? | ABC classes; product clusters; top product pairs by lift and support | `product_abc`, `product_clusters`, `basket_pairs`, `basket_rules`, `basket_top_products` |
| 5. Drivers and risk | What drives value and cancellations? | Value drivers (effect per SD); cancellation odds ratios; model performance | `value_drivers`, `cancellation_odds`, `cancellation_model_performance` |
| 6. Forecast | What comes next? | Weekly actual vs forecasts (test quarter); next-quarter forecast with interval; accuracy table; repeat-purchase gains by decile | `forecast_weekly`, `forecast_next_quarter`, `forecast_accuracy`, `repeat_gains`, `repeat_odds`, `repeat_performance` |
| 7. Anomalies and tests | What is unusual; which differences are real? | Daily residuals with flagged days; top anomalous invoices; flagged-vs-normal profile; hypothesis test results; A/B sample sizes | `anomaly_daily_residuals`, `anomaly_days`, `anomaly_invoices_top`, `anomaly_profile`, `hypothesis_tests`, `bootstrap_intervals`, `ab_sample_size` |

**Style:** a dark theme with light text and the same accent colours as the notebook charts (blue `#64B5F6`, orange
`#FF8A65`, green `#81C784`); one question per page, stated in the page title; units in every axis title.

**Field types to check after connecting:** date columns (`month`, `week`, `date`) as **Date**; shares and rates as
**Percent**; revenue as **Currency (GBP)**.
