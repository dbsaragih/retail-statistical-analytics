# 03 Findings

Analysis notebooks: `notebooks/02_trend_seasonality_py.ipynb` and
`notebooks/02_trend_seasonality_r.ipynb`. Both produce identical results.
Revenue is net product revenue (gross product sales − product cancellations).
Year 1 = Dec 2009 – Nov 2010, Year 2 = Dec 2010 – Nov 2011.

The executive summary will be written once all seven business questions are answered.

## BQ1: How have revenue, orders and customers changed?

**Revenue was flat: +1.9% year on year, with fewer but larger orders.**
Hypothesis (growth driven by more customers): **rejected.**

| Measure | Year 1 | Year 2 | Change |
|---|---|---|---|
| Net revenue | £9.16M | £9.33M | +1.9% |
| Orders (excluding cancelled orders) | 19,603 | 18,837 | −3.9% |
| Value per order | – | – | +5.9% |
| Active customers | 4,239 | 4,293 | +1.3% |

1. **The growth is not statistically real.** A trend with a control for every
   month gives +2.1% a year (p = 0.52), and the moving annual total rose by 2.3%.
   Both agree with the year-on-year figure.
2. **A naive trend line overstates growth tenfold.** A straight-line trend
   gives +21.5% a year and looks significant (p = 0.012), because the series
   starts in a quiet season and ends at the peak. Controlling for Q4 only
   reduces it to +14.6%; controlling for every month removes it. A significant
   p-value does not make a model correct.
3. **The small gain came from bigger orders, not more of them.** Order count
   fell 3.9% while value per order rose 5.9%; active customers were almost
   unchanged (+1.3%).
4. **Winter weakened, the peak strengthened.** Dec–Mar fell 5.4%, Apr–Aug rose
   3.9% and Sep–Nov rose 5.9%. September alone was 20% higher, suggesting the
   pre-Christmas ordering started earlier. April 2011 (−24%) and May 2011 (+21%)
   largely offset each other; a later Easter in 2011 may explain the shift
   (not verifiable in the data).

**So what:** full-year growth depends on the autumn peak. Fewer orders with a
higher value per order is worth investigating: it may mean fewer active small
buyers or a shift toward larger wholesale accounts (see BQ4).

## BQ2: What repeats by month, weekday and hour?

**A strong, regular annual cycle, built around business buyers ordering ahead of Christmas.**
Hypothesis (Q4 peak, weekday and office-hour ordering): **confirmed.**

1. **The year has one peak.** Sep–Nov brings 36–38% of annual net revenue;
   November alone about 15%, the highest month in both years. Oct–Dec together
   bring 35.1%. December is lower because the shop closes over Christmas: the
   weeks starting 28 Dec 2009 and 27 Dec 2010 have no sales at all.
2. **The pattern repeats reliably.** Weekly revenue correlates with itself
   about one year earlier (autocorrelation peak near lag 51–52 weeks), and
   daily sales repeat every six trading days.
3. **Trading follows a business week.** Thursday (£38.9k per trading day),
   Tuesday (£37.3k) and Monday (£36.3k) are strongest; Wednesday and Friday
   about £32k; Sunday about half (£18.0k). The shop is closed on Saturdays
   (the only Saturday sales are from a one-off opening on 5 Dec 2009).
4. **Orders arrive in office hours.** Most revenue comes between 10:00 and
   15:00, with a peak at 12:00 (14.2%).

**So what:** stock, staffing and campaigns should be planned around a
September start of the peak, not October. Forecasts need weekly data with a
yearly pattern and the Christmas closure built in (BQ6).

## Method notes and limitations

- **Two years is the minimum for a yearly pattern.** STL (Python) and classical
  decomposition (R) both overfit: with only two cycles, the seasonal part absorbs
  almost all variation. Seasonal-strength measures are therefore not reported.
- **Complete calendar.** Weeks with no sales are included as zero. Leaving them
  out would shift every later week and distort the seasonal pattern and the
  moving annual total.
- **HAC standard errors** (Newey-West, 4 lags) are used for all trend tests,
  because weekly sales are autocorrelated.
- **Revenue, not profit:** no cost or margin data is available.

### Python–R reconciliation

| Result | Python | R |
|---|---|---|
| Net revenue change | +1.9% | +1.9% |
| Naive trend (p) | +21.5% (0.012) | +21.5% (0.012) |
| Trend with Q4 control | +14.6% | +14.6% |
| Trend with month controls (p) | +2.1% (0.520) | +2.1% (0.520) |
| Moving annual total change | +2.3% | +2.3% |
## BQ3. What drives customer value and cancellations?

Notebooks: [03_drivers_py.ipynb](../notebooks/03_drivers_py.ipynb) and [03_drivers_r.ipynb](../notebooks/03_drivers_r.ipynb).
Both parts use an out-of-time design: features come from Year 1 (Dec 2009 to Nov 2010), and outcomes are measured in Year 2 (Dec 2010 to Nov 2011).

### Part A: Customer value

**Question.** Which Year 1 behaviours predict how much a customer spends in Year 2?

**Data.** 4,227 Year 1 customers (12 dropped with no kept orders). 63.8% bought again in Year 2. Year 2 net revenue per customer is highly skewed: median £308, mean £1,544. The outcome is therefore modelled as log(1 + Year 2 net revenue).

**Method.** Spearman correlation screen; predictors standardised (1 SD); multicollinearity checked with VIF (all below 3.4, none removed); OLS with HC3 robust standard errors.

| Driver (per 1 SD in Year 1) | Effect on Year 2 value | p-value | Reading |
|---|---|---|---|
| Frequency (orders) | +362% | <0.001 | The dominant driver: repeat ordering is the best signal of future value |
| Average order value | +83% | <0.001 | Bigger baskets carry forward |
| Recency (days since last order) | −37% | <0.001 | Customers who went quiet late in Year 1 spend less |
| Tenure (days since first order) | −17% | 0.003 | At the same frequency, newer customers order at a faster rate |
| UK customer | −35% | 0.010 | International customers are worth more, consistent with wholesale buyers abroad |
| Product variety | +8% | 0.218 | Not significant once frequency is controlled |
| Cancellation share | −1% | 0.876 | Not significant; its raw correlation (0.28) only reflects that frequent buyers cancel more often |

R² = 0.347 (adjusted 0.346). Effects are approximate percentage changes in (1 + Year 2 revenue).

**Business reading.** Retention effort should be prioritised by frequency, recency and order value (an RFM view), which BQ4 develops into segments. A customer's cancellation history does not reduce their future value, so cancellations should not be used to downgrade otherwise active customers.

### Part B: Cancellation risk

**Question.** Which order-line characteristics make a cancellation more likely?

**Data.** Product lines with a customer. Train: Year 1, 385,443 lines, cancellation rate 0.88%. Test: Year 2, 374,189 lines, cancellation rate 0.74%.

**Method.** Logistic regression (odds ratios with Wald 95% CIs) and a depth-3 decision tree (balanced classes, at least 500 lines per leaf), both trained on Year 1 and evaluated on Year 2.

| Factor | Odds ratio | 95% CI | Reading |
|---|---|---|---|
| Price outlier (more than 5x or less than 0.2x the item's normal price) | 17.79 | 13.01–24.33 | Mispriced lines are by far the strongest signal |
| log(unit price) | 1.64 | 1.57–1.72 | Doubling the price raises the odds by about 41% |
| log(quantity) | 1.09 | 1.05–1.13 | Doubling the quantity raises the odds by about 6% |
| log(basket size) | 0.65 | 0.63–0.68 | Lines in larger baskets cancel less (about −25% per doubling) |
| UK customer | 0.51 | 0.47–0.57 | Non-UK lines have about twice the odds of cancellation |
| Q4 (Oct–Dec) | 0.80 | 0.74–0.86 | Peak-season lines cancel less |
| Late hour | 1.15 | 1.04–1.28 | Slightly higher risk late in the day |
| log(prior orders) | 1.01 | 0.98–1.04 | No effect |

| Model (Year 2 test) | AUC | Gini | KS |
|---|---|---|---|
| Logistic regression | 0.677 | 0.355 | 0.261 |
| Decision tree | 0.631 | 0.262 | 0.201 |

The tree confirms the same drivers (rpart importance: price 46%, basket size 29%, quantity 17%, UK 8%). Its highest-risk segments in the training data:

| Segment | Lines | Cancellation rate | vs. average (0.88%) |
|---|---|---|---|
| Lower price, larger basket, very large quantity | 1,085 | 5.1% | about 6x |
| Lower price, smaller basket, non-UK | 12,147 | 2.2% | about 2.5x |
| Higher unit price | 70,725 | 1.8% | about 2x |
| Lower price, smaller basket, UK | 131,890 | 0.9% | about average |
| Lower price, larger basket, normal quantity | 169,596 | 0.4% | less than half |

**Business reading.**
- Hypothesis "frequent customers are worth more": **confirmed**.
- Hypothesis "large orders cancel more": **partly rejected**. Large quantities matter only at the extreme; larger baskets actually cancel less. Price, mispricing and non-UK customers are the stronger drivers.
- A price check at order entry (flagging lines far from the item's normal price) would target the single biggest risk factor.
- Predictive power is modest (AUC 0.68): line attributes rank risk but cannot predict individual cancellations. The model suits prioritising checks, not automatic decisions.

### Python–R reconciliation (BQ3)

| Result | Python | R |
|---|---|---|
| Customers used / bought again | 4,227 / 63.8% | 4,227 / 63.8% |
| OLS coefficients, robust SE, R² | identical (R² 0.347) | identical |
| Logistic odds ratios and CIs | identical | identical |
| Logistic AUC / Gini / KS | 0.677 / 0.355 / 0.261 | 0.677 / 0.355 / 0.261 |
| Tree splits | identical | identical |
| Tree AUC / Gini / KS | 0.631 / 0.262 / 0.201 | 0.631 / 0.262 / 0.201 |

Implementation notes: sklearn's `class_weight="balanced"` corresponds to rpart's `prior = c(0.5, 0.5)`. rpart needs `cp = -1` to keep splits whose two children predict the same class, as sklearn does; with `cp = 0` the tree was smaller and its test AUC fell to 0.619. Tree variable importance is defined differently in the two libraries (rpart includes surrogate splits), so importance shares differ slightly.

## BQ4. Which customer and product segments exist, and how much does each bring?

Notebooks: [04_segmentation_py.ipynb](../notebooks/04_segmentation_py.ipynb) and [04_segmentation_r.ipynb](../notebooks/04_segmentation_r.ipynb).
Window: Year 2 (1 Dec 2010 to 30 Nov 2011). Net revenue = gross product sales minus product cancellations, rounded to the penny.

### Part A: Customers

4,293 identified customers bought in Year 2; 13 with net revenue of zero or less (everything cancelled) are excluded, leaving 4,280.

**RFM segments** (recency, frequency and monetary value scored 1–5 by quintile):

| Segment | Customers | Share of customers | Share of net revenue | Median days since last purchase | Median purchase days | Median net revenue |
|---|---|---|---|---|---|---|
| Champions | 1,087 | 25% | **68%** | 11 | 6 | £2,129 |
| Loyal | 814 | 19% | 13% | 38 | 3 | £817 |
| New or promising | 333 | 8% | 2% | 17 | 1 | £301 |
| Needs attention | 334 | 8% | 2% | 51 | 1 | £325 |
| At risk | 667 | 16% | 9% | 135 | 3 | £712 |
| Hibernating | 1,045 | 24% | 5% | 225 | 1 | £253 |

**K-means clusters** on log recency, frequency and monetary value (standardised). k = 2 to 8 were tested;
k = 2 has the highest silhouette (0.43) but only separates active from lapsed customers. Among k ≥ 3, k = 4 has the
best silhouette (0.34) and sits at the bend of the elbow curve, so k = 4 was chosen.

| Cluster | Name | Customers | Share of net revenue | Median days since last purchase | Median purchase days | Median net revenue |
|---|---|---|---|---|---|---|
| 1 | VIP regulars | 17% | **65%** | 9 | 8 | £3,300 |
| 2 | Mid-value, cooling | 29% | 24% | 55 | 3 | £1,180 |
| 3 | Recent newcomers | 18% | 5% | 15 | 2 | £400 |
| 4 | Lapsed one-timers | 35% | 6% | 179 | 1 | £270 |

The clusters and the RFM rules broadly agree (cluster 1 is 95% Champions; cluster 4 is two-thirds Hibernating).
K-means adds one insight: cluster 2 combines 421 of the 667 At-risk customers with 270 Champions. These are
mid-value customers who are buying less often, the clearest win-back target.

**Business reading.**
- Revenue is highly concentrated: one customer in six (VIP regulars) brings in about two-thirds of net revenue. Protecting them (service, stock availability, account management) matters more than acquiring new low-value buyers.
- Cluster 2 (£1.9m) is the main retention opportunity: a re-engagement campaign aimed at customers whose last order was one to four months ago.
- Recent newcomers should be nurtured towards a second and third order; BQ3 showed that order frequency is the strongest predictor of next-year value.
- Lapsed one-timers (35% of customers, 6% of revenue) justify only low-cost reactivation such as email.

### Part B: Products

**ABC classification** by net revenue:

| Class | Products | Share of products | Share of net revenue | Median price | Median customers |
|---|---|---|---|---|---|
| A | 837 | 21% | 80% | £2.55 | 166 |
| B | 979 | 25% | 15% | £1.65 | 64 |
| C | 2,081 | 53% | 5% | £2.10 | 8 |

**K-means clusters** (products with at least 20 orders) on log net revenue, log customers, log price and the
October–December share of sales. k = 3 and k = 4 have almost the same silhouette (0.281 and 0.278); k = 4 was
chosen because it separates seasonal products, which need their own stock planning.

| Cluster | Name | Products | Share of net revenue | Median customers | Median price | Q4 share of sales |
|---|---|---|---|---|---|---|
| 1 | Core bestsellers | 31% | **78%** | 148 | £2.95 | 29% |
| 2 | Seasonal (Christmas) lines | 17% | 10% | 57 | £2.08 | **75%** |
| 3 | Low-price volume items | 29% | 9% | 55 | £0.83 | 25% |
| 4 | Niche items | 23% | 4% | 17 | £2.95 | 29% |

**Business reading.**
- One product in five makes 80% of revenue; stock-outs of A-class products and core bestsellers carry the largest revenue risk.
- More than half of the catalogue (C class) brings in 5% of revenue, a candidate for range rationalisation.
- Seasonal lines sell three-quarters of their volume in October–December; buying for them must be committed well before Q4 (see the seasonality in BQ2).

### Python–R reconciliation (BQ4)

| Result | Python | R |
|---|---|---|
| Customers used | 4,280 | 4,280 |
| RFM scores and segments | identical | identical |
| Customer k-means, k = 4 within-cluster SS | 3,937.37 | 3,937.15 |
| Customers in the same cluster | 99.6% | |
| ABC classes | identical | identical |

Implementation notes:
- Net revenue is rounded to the penny before filtering. Without rounding, floating-point residue left two fully cancelled customers with a "positive" net revenue of about £0.000000000001 in Python, but exactly zero in R. That changed every customer's rank.
- RFM ties are broken by customer ID, so the quintile scores are identical in both languages.
- R's `kmeans()` (Hartigan–Wong algorithm) found a marginally better solution than scikit-learn (Lloyd's algorithm), so about 0.4% of borderline customers fall in a different cluster. The cluster profiles are practically the same.
