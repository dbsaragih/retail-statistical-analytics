# Retail Statistical Analytics

End-to-end statistical analysis of two years of transactions from a UK online
gift retailer: trends, seasonality, drivers, segmentation, market-basket
analysis, forecasting, classification, anomaly detection, hypothesis testing
and experiment design.

## Progress

| Stage | Output | Status |
|---|---|---|
| 1. Project setup | Folder structure, `.gitignore`, `src/download_data.py`, Python environment | ✅ Done |
| 2. Version control | Git history on GitHub | ✅ Done |
| 3. Problem framing | [docs/01_problem_statement.md](docs/01_problem_statement.md) | ✅ Done |
| 4. Data profiling | [notebooks/01_profiling.ipynb](notebooks/01_profiling.ipynb) | ✅ Done |
| 5. Data quality review | [docs/02_data_quality_findings.md](docs/02_data_quality_findings.md), decision log T1–T17 | ✅ Done |
| 6. Data cleaning | [src/clean_data.py](src/clean_data.py) → `data/processed/`, 18 output checks | ✅ Done |
| 7. R environment | [r/install_packages.R](r/install_packages.R), R Jupyter kernel | ✅ Done |
| 8. BQ1–BQ2 Trend and seasonality | [Python](notebooks/02_trend_seasonality_py.ipynb), [R](notebooks/02_trend_seasonality_r.ipynb), [findings](docs/03_findings.md)| ✅ Done |
| 9. BQ3: Drivers of value and cancellation | [Python](notebooks/03_drivers_py.ipynb), [R](notebooks/03_drivers_r.ipynb), [findings](docs/03_findings.md) | ✅ Done |
| 10. BQ4 Segmentation | [Python](notebooks/04_segmentation_py.ipynb), [R](notebooks/04_segmentation_r.ipynb), [findings](docs/03_findings.md) | ✅ Done |
| 11. BQ5 Market basket | [Python](notebooks/05_market_basket_py.ipynb), [R](notebooks/05_market_basket_r.ipynb), [findings](docs/03_findings.md) | ✅ Done |
| 12. BQ6 Forecasting and repeat purchase | [Python](notebooks/06_forecast_repeat_py.ipynb), [R](notebooks/06_forecast_repeat_r.ipynb), [findings](docs/03_findings.md) | ✅ Done |
| 13. BQ7 Anomalies | [Python](notebooks/07_anomalies_py.ipynb), [R](notebooks/07_anomalies_r.ipynb), [findings](docs/03_findings.md) | ✅ Done |
| 14. BQ8 Hypothesis testing and experiment design | [Python](notebooks/08_hypothesis_ab_py.ipynb), [R](notebooks/08_hypothesis_ab_r.ipynb), [findings](docs/03_findings.md) | ✅ Done |
| 15. Python–R reconciliation | [docs/04_reconciliation.md](docs/04_reconciliation.md) | ✅ Done |
| 16. Findings | [docs/03_findings.md](docs/03_findings.md): executive summary, recommendations, BQ1–BQ8 | ✅ Done |
| 17. Dashboard | [Looker Studio report](https://datastudio.google.com/reporting/f4108bc3-ed9f-4531-ad69-5212a8e33b36) (7 pages), [setup and design](docs/05_dashboard.md), [src/publish_to_sheets.py](src/publish_to_sheets.py) | ✅ Done |
| 18. Client deliverable and presentation | Public previews: [Excel workbook](reports/deliverables/retail_analytics_client_workbook__.xlsx) (Summary and BQ1–BQ3; built by [src/build_workbook.py](src/build_workbook.py)) and [findings deck](reports/deliverables/retail_analytics_findings__.pptx) (first 4 of 13 slides). Full versions available on request | ✅ Done |
| 19. Reproducibility | `requirements.txt`, final README | ⬜ Planned |

## Dashboard

An interactive [Looker Studio report](https://datastudio.google.com/reporting/f4108bc3-ed9f-4531-ad69-5212a8e33b36) presents the results in seven pages, one question each:

| Page | Question |
|---|---|
| 1. Overview | How is the business doing? |
| 2. Seasonality | When do customers buy? |
| 3. Customers | Who are the customers? |
| 4. Products | What sells, and together? |
| 5. Drivers and risk | What drives value and cancellations? |
| 6. Forecast | What comes next? |
| 7. Anomalies and tests | What is unusual, and which differences are real? |

![Dashboard overview](reports/figures/dashboard/page1_overview.png)

The notebooks write summary tables to `reports/dashboard_data/`; `src/publish_to_sheets.py` copies them to a Google
Sheet that the report reads. See [docs/05_dashboard.md](docs/05_dashboard.md).

## Data and licence

Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository.
https://doi.org/10.24432/C5CG6D

Used under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
licence. The data is not stored in this repository; run
`python src/download_data.py` to download it.