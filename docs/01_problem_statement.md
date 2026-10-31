# 01 Problem statement

## 1. Context

The client is a UK-based online retailer selling all-occasion giftware, with
many wholesale customers. It has two years of transaction data
(1 December 2009 – 9 December 2011) and wants to understand how the business
behaves over time, who its customers are, what they buy together, and what to
expect next, so it can plan stock, marketing and customer retention.

**Stakeholders:** Managing Director, Head of Marketing, Head of Operations.

## 2. Business questions

| # | Question | Decision it supports | Hypothesis | Methods |
|---|---|---|---|---|
| BQ1 | How have revenue, orders and active customers changed over the two years? | Growth targets and budget | Revenue grew year on year, driven more by the number of customers than by order size | Time-series plots, moving averages, trend regression, decomposition |
| BQ2 | What repeats by month, weekday and hour? | Stock build-up, staffing, campaign timing | Sales peak strongly in Q4 (gift season); orders concentrate on weekdays and office hours, consistent with business buyers | Seasonal decomposition, autocorrelation, seasonal comparisons |
| BQ3 | Which factors relate to customer value and to order cancellation? | Where to focus retention and process fixes | Customer value is driven mainly by purchase frequency; cancellations are more likely for large orders | Correlation, linear and logistic regression, decision tree |
| BQ4 | Which customers and which products behave similarly? | Targeted marketing and assortment planning | A small group of frequent, high-spending customers generates most revenue; products split into year-round and seasonal groups | RFM features, k-means, hierarchical clustering |
| BQ5 | Which products are bought together? | Bundles, cross-selling, website recommendations | Strong pairs exist within product families (same design in different colours or sizes) | Association rules (Apriori / FP-Growth): support, confidence, lift |
| BQ6 | What will weekly revenue be over the next quarter, and which customers will buy again? | Stock planning and retention campaigns | A seasonal model beats a naive benchmark; recent and frequent customers are most likely to return | SARIMA, ETS, Prophet vs seasonal naive; logistic regression, decision tree, gradient boosting |
| BQ7 | Which transactions and days are unusual? | Fraud and data-quality controls, early warning | Unusual cases are concentrated in very large quantities, cancellations and non-product codes | Outlier analysis (IQR), control charts, Isolation Forest |

## 3. Key definitions

To be confirmed during data profiling (docs/02).

| Term | Definition |
|---|---|
| Transaction line | One row: one product on one invoice |
| Invoice (order) | All lines sharing an invoice number |
| Cancellation | An invoice whose number starts with "C" (negative quantities) |
| Revenue | Quantity × Price on non-cancelled lines with positive quantity and price, excluding non-product codes |
| Non-product code | Stock codes that are not goods, such as postage, fees and manual adjustments (list fixed in profiling) |
| Customer | A non-missing Customer ID; lines without one are used for sales trends and baskets, not for customer analysis |
| Basket | The set of distinct products on one non-cancelled invoice |
| Repeat buyer (BQ6) | A customer who purchases again within 90 days after a cut-off date |

## 4. Scope

- **Period:** 1 Dec 2009 – 9 Dec 2011. December 2011 is incomplete, so it is
  excluded from month-on-month and year-on-year comparisons.
- **Currency:** prices in GBP (£), as recorded.
- **Out of scope:** profit and margin (no cost data), marketing spend, and
  external drivers such as promotions or price changes.

## 5. Known limitations

- About two years of history: yearly seasonality is observed only twice, so
  forecasting focuses on weekly data.
- A share of lines has no Customer ID; customer-level results cover identified
  customers only.
- No cost or margin data: "value" means revenue, not profit.

## 6. Deliverables

1. Data quality findings and decision log (docs/02)
2. Analysis notebooks answering BQ1–BQ7 (notebooks/)
3. Findings document with an executive summary (docs/03)
4. Short presentation deck

## Data and licence

Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository.
https://doi.org/10.24432/C5CG6D. Used under CC BY 4.0.