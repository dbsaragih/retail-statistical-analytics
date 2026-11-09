# Retail Statistical Analytics

End-to-end statistical analysis of two years of transactions from a UK online
gift retailer: trends, seasonality, drivers, segmentation, market-basket
analysis, forecasting, classification and anomaly detection.

## Progress

| Stage | Output | Status |
|---|---|---|
| 1. Project setup | Folder structure, `.gitignore`, `src/download_data.py`, Python environment | ✅ Done |
| 2. Version control | Git history on GitHub | ✅ Done |
| 3. Problem framing | [docs/01_problem_statement.md](docs/01_problem_statement.md) | ✅ Done |
| 4. Data profiling | [notebooks/01_profiling.ipynb](notebooks/01_profiling.ipynb) | ✅ Done |
| 5. Data quality review | [docs/02_data_quality_findings.md](docs/02_data_quality_findings.md), decision log T1–T12 | ✅ Done |
| 6. Data cleaning | [src/clean_data.py](src/clean_data.py) → `data/processed/` | ✅ Done |
| 7. R environment | `r/install_packages.R`, R Jupyter kernel | ⏳ In progress |
| 8. BQ1–BQ2 Trend and seasonality | `notebooks/02_trend_seasonality_py.ipynb`, `_r.ipynb` | ⏳ In progress |
| 9. BQ3 Drivers of value and cancellation | Regression and decision tree, Python and R | ⬜ Planned |
| 10. BQ4 Segmentation | Customer and product clustering, Python and R | ⬜ Planned |
| 11. BQ5 Market basket | Association rules, Python and R | ⬜ Planned |
| 12. BQ6 Forecasting and repeat purchase | SARIMAX, ETS, Prophet vs benchmark; classification model | ⬜ Planned |
| 13. BQ7 Anomalies | Outliers, control charts, Isolation Forest | ⬜ Planned |
| 14. Python–R reconciliation | Both languages agree on every key number | ⬜ Planned |
| 15. Findings | `docs/03_findings.md` with executive summary | ⬜ Planned |
| 16. Dashboard | Looker Studio report on Google Sheets summary tables | ⬜ Planned |
| 17. Client deliverable and presentation | Excel workbook (Google Sheets compatible), short deck | ⬜ Planned |
| 18. Reproducibility | `requirements.txt`, final README | ⬜ Planned |

## Data and licence

Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository.
https://doi.org/10.24432/C5CG6D

Used under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
licence. The data is not stored in this repository; run
`python src/download_data.py` to download it.