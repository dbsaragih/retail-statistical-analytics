# 02 Data quality findings and decision log

Source: `notebooks/01_profiling.ipynb` (read-only profiling of the raw data).

## 1. Summary

The raw data is complete in its key fields but needs eleven treatments before
analysis. Two issues would materially distort results if left untreated:

1. **The two source sheets overlap.** Transactions dated 1–9 December 2010
   appear in both yearly sheets: 22,844 extra copies, about £440k of revenue,
   which would create a false December 2010 sales spike.
2. **Cancellations must be netted off.** Dropping only the cancellation lines
   would keep the cancelled orders as sales. Product cancellations total
   £716k, 3.6% of gross product sales (the raw cancelled value of £1.53M also
   includes non-product entries such as manual adjustments and fees).
   Revenue is therefore reported net of cancellations.

## 2. Dataset reconciliation

| Item | Value |
|---|---|
| Rows (both sheets) | 1,067,371, matching the UCI source |
| Period | 1 Dec 2009 07:45 – 9 Dec 2011 12:50 |
| Gross positive revenue (all lines, before treatment) | £20,972,968 |
| Distinct customers | 5,942 |
| Countries | 43 (United Kingdom 85.2% of revenue) |

## 3. Findings

Shares are of all rows and of gross positive revenue.

| # | Finding | Rows | Revenue touched |
|---|---|---|---|
| F1 | Exact duplicate rows: 22,844 inside the 1–9 Dec 2010 sheet overlap, 11,491 elsewhere | 34,335 (3.2%) | £496k (2.4%) |
| F2 | Cancellation invoices (number starts with "C") | 19,494 (1.8%) | £1.53M cancelled (7.3%) |
| F3 | Only 40.4% of cancellation lines match an order exactly (same customer, product, quantity); the rest are partial cancellations, orders before Dec 2009, or lines without a customer | – | – |
| F4 | The two largest orders (74,215 and 80,995 units) were cancelled within 16 minutes | 4 | £245k gross |
| F5 | Negative quantities on normal invoices, all at zero price (verified for all 3,457) and without a customer ("lost", "damages", "wrongly marked"): stock adjustments, not returns | 3,457 (0.3%) | £0 |
| F6 | Zero price, 99% without a customer | 6,202 (0.6%) | £0 |
| F7 | "A" invoices: bad-debt adjustments with prices down to −£53,594 | 6 | −£148k |
| F8 | Non-product stock codes: postage and carriage, marketplace fees, bank charges, charity commission, manual entries, discounts, samples, vouchers, test products | 6,094 (0.6%) | £864k positive (4.1%) |
| F9 | Some real products use non-standard codes (`DCGS...`, `SP1002`); some codes carry trailing spaces | – | – |
| F10 | Missing Customer ID | 243,007 (22.8%) | £3.23M (15.4%) |
| F11 | Genuine wholesale lines up to 19,152 units at £0.10; the 99th percentile of quantity is 100 units | Few | – |
| F12 | Saturday is effectively closed (402 rows vs about 190,000 on other weekdays); trading hours 06:00–21:00 | – | – |
| F13 | December 2011 covers only 8 trading days | 25,526 | – |
| F14 | 1,232 stock codes have more than one description, often warehouse notes ("found", "wrongly coded-23343") | – | – |
| F15 | `Customer ID` is stored as a decimal number; 4,382 rows have no description | – | – |
| F16 | Near-duplicates: same invoice, product, quantity, price, time and customer, but a different description (products renamed during entry) | 2 | £552 |
| F17 | Descriptions with leading/trailing spaces (213,035) or internal double spaces (48,398); 79 contain non-ASCII characters | 213,035 | – |
| F18 | All 4,382 rows without a description are zero-priced | 4,382 | £0 |
| F19 | Country variants (EIRE, RSA, USA) and placeholders (Unspecified, European Community) | 808 unknown after cleaning | – |
| F20 | Product lines priced above 5× or below 0.2× their product's median price, e.g. a £0.42 car flag at £1,157 | 3,156 | £131k (0.67% of gross product sales) |
| F21 | Cancellations without an exact matching order (partial cancellations, orders before Dec 2009, no customer) | 12,773 of 19,104 | – |

## 4. Decision log

| ID | Finding | Treatment | Effect |
|---|---|---|---|
| T1 | F1 | Remove exact duplicate rows | Fixes the sheet overlap; the copies outside it are immaterial (0.27% of revenue) |
| T2 | F7 | Exclude "A" invoices | Accounting entries, not sales |
| T3 | F5 | Exclude negative-quantity lines that are not on a "C" invoice | Stock adjustments, zero value |
| T4 | F6 | Exclude zero-price lines from revenue and baskets | No sale took place |
| T5 | F2–F4 | Keep cancellations in a separate table. Report **net revenue = gross sales − cancellations**. For transaction-level analysis (baskets, outliers), remove orders with an exact matching cancellation | Cancelled orders never count as sales |
| T6 | F8, F9 | Classify non-product codes with an explicit list (below); every other code is a product. Exclude non-products from product revenue; report shipping income separately | Product format is unreliable, so a list is used instead of a pattern |
| T7 | F10 | Keep lines without a Customer ID for trends, seasonality, forecasting and baskets; exclude them from customer analyses (value drivers, segmentation, repeat-purchase model) | Customer results cover identified customers only |
| T8 | F14 | Use the most frequent description per stock code as the product name | Clean product names |
| T9 | F11 | Keep genuine wholesale lines; flag them; use log scales or robust methods in models; examine them in BQ7 | Real business, not errors |
| T10 | F13 | Exclude December 2011 from monthly and year-on-year comparisons; forecast on complete weeks | Avoids a false drop at the end |
| T11 | F12 | Treat the trading week as six days (Saturday closed) | Correct weekly seasonality |
| T12 | F9, F15 | Strip spaces from stock codes; store `Customer ID` as an integer that allows missing values | Correct joins and types |
| T13 | F16 | Keep near-duplicates; monitor their count in the output checks | Immaterial, and possibly genuine repeat lines; T8 gives both copies the same product name |
| T14 | F17 | Strip and collapse spaces in descriptions before naming products; keep non-ASCII characters (e.g. "£") | Consistent product names; no hidden duplicates were revealed (0 rows) |
| T15 | F19 | Map EIRE → Ireland, RSA → South Africa, USA → United States; flag placeholders as unknown (`country_known`); add `is_uk` | Clean country analysis; unknown countries are kept but can be filtered |
| T16 | F20 | Flag price outliers (`is_price_outlier`, `price_ratio`) and keep them in revenue; use as a sensitivity check in price-related analyses | Immaterial (0.67%), and errors cannot be separated from genuine special pricing |
| T17 | F21 | Flag each cancellation as matched or unmatched (`cancellation_matched`) | Revenue is unaffected (net of all cancellations); the flag supports cancellation analysis |

### Non-product code list (T6)

| Group | Codes |
|---|---|
| Shipping (reported separately) | POST, DOT, C2, C3 |
| Fees and charges | AMAZONFEE, BANK CHARGES, CRUK |
| Adjustments and manual entries | M, m, D, S, B, ADJUST, ADJUST2 |
| Gift vouchers | all codes starting with `gift_` |
| Test products | TEST001, TEST002 |

## 5. Revenue definitions after treatment

| Measure | Definition |
|---|---|
| Gross product sales | Quantity × Price on cleaned, non-cancelled product lines |
| Cancellations | Absolute value of cancellation lines for products |
| **Net revenue** | Gross product sales − cancellations |
| Shipping income | Lines with shipping codes, reported separately |

## 6. Verified items and limitations

Verified after the checklist review:
- T3 removes stock adjustments only: none of the 3,457 lines has a price (F5).
- No lines have quantity 0.
- Missing descriptions are all zero-priced and removed by T4 (F18).
- Trailing spaces in stock codes (e.g. `47503J`) are stripped (T12).
- Saturday sales occur on one date only (5 Dec 2009, 400 lines): the shop is
  closed on Saturdays (T11).

Limitations:
- Staff or internal accounts cannot be identified; no field marks them.
- Returns appear only as cancellation invoices; there is no separate returns flow.
- Near-duplicates (2 lines, £552) are kept because they may be genuine (T13).
- Timestamps are taken as UK local time.

## 7. Cleaning results

Produced by `src/clean_data.py`.

| Step | Rows removed | Rows remaining |
|---|---|---|
| Raw data | – | 1,067,371 |
| T1 Exact duplicates | 34,335 | 1,033,036 |
| T2 "A" bad-debt adjustments | 6 | 1,033,030 |
| T3 Stock adjustments | 3,393 | 1,029,637 |
| T4 Zero-price lines | 2,621 | 1,027,016 |
| T14 Duplicates revealed by text normalisation | 0 | 1,027,016 |

Counts for T3 and T4 are below the profiling figures because earlier steps had
already removed overlapping rows.

**Split:** 1,007,912 sales lines + 19,104 cancellation lines = 1,027,016.

| Revenue (GBP) | Amount |
|---|---|
| Gross product sales | 19,643,862 |
| Less product cancellations | 716,463 |
| **Net product revenue** | **18,927,399** |
| Shipping income (separate) | 448,963 |

| Flag | Count |
|---|---|
| Sales lines with a customer | 77.3% |
| Sales lines from the UK | 91.9% |
| Sales lines with unknown country | 808 |
| Bulk lines (quantity > 500) | 952 |
| Price outlier lines | 3,156 (£131,043 gross; 60 later cancelled) |
| Orders with an exact matching cancellation (one-to-one) | 6,331 |
| Cancellation lines without a matching order | 12,773 |
| Sales lines in December 2011 (partial month) | 24,834 |

The one-to-one match rate (34.4% of cancellations with a customer) is lower
than the profiling estimate (40.4%) because each cancellation now flags only
one order, the order must precede the cancellation, and duplicates are removed.

## 8. Output checks

`src/clean_data.py` runs 18 checks before saving (C01–C18), one or more per
decision. Every check runs; the script stops without saving if any fails.
Two monitoring lines are reported but not enforced: product lines without a
name (0) and near-duplicates (2 lines, £552).