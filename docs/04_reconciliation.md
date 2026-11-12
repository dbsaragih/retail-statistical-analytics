# 04 Python–R reconciliation

Every business question is answered twice, once in Python and once in R, from the same cleaned data
(`data/processed/`, produced once by `src/clean_data.py`). Each R notebook ends with a cell that reads the Python
results and compares them. This document summarises those checks.

## How results are compared

| Level | Applies to | Standard |
|---|---|---|
| **Exact** | Counts, sums, closed-form statistics (OLS, logistic regression, tests, rules, scores) | Identical, apart from rounding in the exported CSV files (6 decimals) |
| **Close** | Models fitted by numerical optimisation with different optimisers (ARIMA errors) | Same model; differences in the third decimal |
| **Approximate** | Randomised methods (k-means starts, Isolation Forest, bootstrap) | Same conclusions; agreement measured by overlap or rank correlation |

## Results by business question

| BQ | Result | Python | R | Level | Agreement |
|---|---|---|---|---|---|
| BQ1 | Net revenue change, trend with month controls (p), moving annual total | +1.9%, +2.1% (0.520), +2.3% | same | Exact | Identical |
| BQ1 | Naive trend and trend with Q4 control (HAC standard errors) | +21.5% (p 0.012), +14.6% | same | Exact | Identical |
| BQ2 | Monthly, weekday and hourly profiles | — | — | Exact | Identical |
| BQ2 | Seasonal decomposition | STL | Classical `decompose()` | Different methods | Both overfit with two cycles; not reported (see BQ2 notes) |
| BQ3 | OLS coefficients, HC3 robust SE, R² 0.347 | — | — | Exact | Identical |
| BQ3 | Logistic odds ratios and Wald CIs; AUC 0.677 | — | — | Exact | Identical |
| BQ3 | Decision tree splits; AUC 0.631 | sklearn | rpart | Exact | Identical splits and AUC |
| BQ4 | RFM scores, segments, ABC classes | — | — | Exact | Identical |
| BQ4 | Customer k-means (k = 4) | SS 3,937.37 | SS 3,937.15 | Approximate | 99.6% of customers in the same cluster |
| BQ5 | Association rules (support ≥ 1%, confidence ≥ 30%) | 1,488 rules (mlxtend) | 1,488 rules (arules) | Exact | Same rules; largest difference 5 × 10⁻⁷ |
| BQ6 | Naive, seasonal naive, Fourier regression, Prophet accuracy | — | — | Exact | Differences below 0.0001 |
| BQ6 | Fourier + AR(1) errors | SARIMAX | `arima()` | Close | MAE differs by 0.05 (£k) |
| BQ6 | Logistic regression, decision tree, XGBoost; gains table | AUC 0.748 / 0.724 / 0.740 | same | Exact | Identical |
| BQ7 | Daily residuals, z-scores, control limits, flagged days | 7 days | 7 days | Exact | Identical dates |
| BQ7 | Isolation Forest scores | scikit-learn | isotree | Approximate | Rank correlation 0.989; 89% of the top 1% shared |
| BQ8 | t, Mann–Whitney U, z and chi-square tests; sample sizes | — | — | Exact | Identical (relative difference below 4 × 10⁻⁸) |
| BQ8 | Bootstrap 95% intervals | — | — | Approximate | Within £2.5 |

## What it took to make the languages agree

Most differences between Python and R come from defaults, not from the statistics. These settings made the results
match, and they are worth reusing in any two-language project:

| Issue | Symptom | Fix |
|---|---|---|
| Floating-point residue in money | Fully cancelled customers had net revenue of 0.000000000001 in Python but 0 in R, which changed every rank (BQ4); tied order values differed (BQ8) | Round money to the penny before filtering, ranking or rank-based tests |
| Ties in ranks and quintiles | Different tie handling gives different scores | Sort by an ID and break ties by order (`method="first"` / `ties.method = "first"`) |
| Text sorting | R sorts by locale, Python by code point | Use C-locale sorting in R (`sort(method = "radix")`) for keys |
| Standard deviation | pandas and `scale()` default to different denominators | State the denominator explicitly (population or sample) |
| Robust standard errors | Different HAC defaults | Newey-West with 4 lags, no prewhitening, normal reference (`df = Inf`) in R |
| Decision trees | rpart stops splits that do not change the predicted class | `cp = -1` and equal class priors to match sklearn's balanced weights |
| Association rules | mlxtend allows several products on the right-hand side, arules one | Keep single-product consequents in Python |
| Missing calendar weeks | Closed weeks absent from the data shift later weeks | Build a complete calendar with zeros before any time-series work |
| XGBoost | Multi-threading and sampling make runs differ | Exact tree method, no row or column sampling, one thread |
| k-means | Lloyd's (sklearn) and Hartigan–Wong (R) reach slightly different optima | Many random starts; compare cluster profiles and overlap, not labels |

## Environment

Both languages run in WSL (Ubuntu 24.04 on Windows): Python 3.12 in a virtual environment and R 4.6 with the
packages in `r/install_packages.R`, each as a Jupyter kernel in VS Code. Git runs from Windows.
