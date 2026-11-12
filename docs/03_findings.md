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

## BQ5. Which products are bought together?

Notebooks: [05_market_basket_py.ipynb](../notebooks/05_market_basket_py.ipynb) and [05_market_basket_r.ipynb](../notebooks/05_market_basket_r.ipynb).

**Data.** A basket is one Year 2 invoice (1 Dec 2010 to 30 Nov 2011) with the distinct products ordered; lines later
cancelled with an exact match are removed. 18,837 baskets, 3,901 products. Baskets are large, as expected for a
wholesale-heavy business: median 15 distinct products, mean 26; only 7.5% contain a single product, and about 600
contain 100 or more.

**Method.** Frequent itemsets (FP-Growth in Python, Apriori in R) and association rules `{A} → {B}` with support ≥ 1%
(at least 189 baskets), confidence ≥ 30% and at most three products per rule.

| Result | Value |
|---|---|
| Products in at least 1% of baskets | 814 |
| Frequent itemsets | 1,933 (814 single, 863 pairs, 256 triples) |
| Rules | 1,488 (731 with one product on the left, 757 with two) |
| Distinct product pairs | 491 |
| Lift | median 9.3, maximum 78.9 |
| Confidence | median 51% |

The most frequent single product is the WHITE HANGING HEART T-LIGHT HOLDER (11.3% of baskets), followed by JUMBO BAG
RED RETROSPOT (10.8%) and REGENCY CAKESTAND 3 TIER (10.0%).

**Strongest links (highest lift).** The HERB MARKER range (thyme, rosemary, parsley, basil, mint) dominates: any two
markers appear together about 73–77 times more often than chance, and a customer who buys one marker buys a second
in about 90% of cases. Customers buy the set, not single items.

| Product A | Product B | Baskets with both | A → B | B → A | Lift |
|---|---|---|---|---|---|
| Herb marker thyme | Herb marker rosemary | 1.1% | 93% | 93% | 76.8 |
| Set of 3 wooden tree decorations | Set of 3 wooden stocking decorations | 1.0% | 73% | 68% | 47.8 |
| Regency tea plate green | Regency tea plate pink | 1.4% | 72% | 91% | 47.4 |
| Regency sugar bowl green | Regency milk jug pink | 1.2% | 75% | 73% | 45.2 |
| Jam jar with pink lid | Jam jar with green lid | 1.2% | 66% | 74% | 42.0 |
| Childrens cutlery Dolly Girl | Childrens cutlery Spaceboy | 1.1% | 76% | 62% | 41.6 |

**Most common combinations (highest support).**

| Product A | Product B | Baskets with both | A → B | B → A | Lift |
|---|---|---|---|---|---|
| Jumbo bag pink polkadot | Jumbo bag red retrospot | 4.3% | 68% | 40% | 6.3 |
| Green Regency teacup and saucer | Roses Regency teacup and saucer | 3.9% | 75% | 72% | 13.8 |
| Jumbo storage bag Suki | Jumbo bag red retrospot | 3.7% | 61% | 34% | 5.6 |
| Jumbo shopper vintage red paisley | Jumbo bag red retrospot | 3.5% | 58% | 32% | 5.4 |
| Lunch bag red retrospot | Lunch bag Suki design | 3.4% | 42% | 51% | 6.4 |

Confidence is not symmetric. 68% of baskets with the pink polkadot jumbo bag also contain the red retrospot one,
but only 40% of red retrospot baskets contain the pink one: the red retrospot bag is the anchor product of the range.

**Hypothesis.** "Strong pairs exist within product families (same design in different colours or sizes)":
**confirmed**. Almost all top rules link variants of one range: herb markers, Regency teaware colours, jam jar lid
colours, children's cutlery designs, jumbo and lunch bag prints, Christmas wooden decorations.

**Business reading.**
- **Bundles:** sell the herb markers as a set and the Regency teaware as mixed-colour sets; customers already buy them that way.
- **"Complete the set" recommendations:** when a basket contains one variant, suggest the others in the range (for example pink polkadot jumbo bag → red retrospot, 68%).
- **Stock planning:** variants of one range sell together, so a stock-out of one colour can hold back the whole order; replenish ranges together.
- **Merchandising:** list range variants next to each other on the website and in the wholesale catalogue.

**Limitations.** Association is not causation: a rule shows what is bought together, not that recommending B will
increase sales (BQ8 sets out how to test that). The 1% support threshold hides rarer but possibly valuable
combinations, and the large wholesale baskets raise co-occurrence for popular items.

### Python–R reconciliation (BQ5)

| Result | Python (mlxtend) | R (arules) |
|---|---|---|
| Baskets | 18,837 | 18,837 |
| Rules | 1,488 | 1,488 |
| Rules found by only one language | 0 | 0 |
| Largest difference in support, confidence, lift | 5 × 10⁻⁷ (CSV rounding to 6 decimals) | |
| Largest difference in basket count | 0 | |

Implementation notes: `mlxtend` can produce rules with several products on the right-hand side, while `arules` always
has one, so Python keeps single-product consequents only. Rules are matched by a key of stock codes sorted in C-locale
order, which is the same in both languages.

## BQ6. What will weekly revenue be next quarter, and which customers will buy again?

Notebooks: [06_forecast_repeat_py.ipynb](../notebooks/06_forecast_repeat_py.ipynb) and [06_forecast_repeat_r.ipynb](../notebooks/06_forecast_repeat_r.ipynb).

### Part A: Weekly revenue forecast

**Data and design.** 104 complete weeks of net revenue (7 Dec 2009 to 28 Nov 2011, £ thousand), closed weeks set to 0.
The last 13 weeks (5 Sep to 28 Nov 2011) are held out as a test quarter; models are trained on the 91 weeks before.
Two dummies mark the partly open and the closed Christmas weeks.

**Models.** Naive (last value), seasonal naive (same week last year, the benchmark), Fourier regression (trend,
Christmas dummies and K yearly sine/cosine pairs), the same regression with AR(1) errors (SARIMAX with Fourier
regressors) and Prophet (piecewise-linear trend with changepoints, 10 yearly Fourier pairs and the Christmas dummies).
K was chosen by AIC: K = 10, the largest value tested.

ETS and 52-week seasonal ARIMA were not used: two yearly cycles are too few to estimate them reliably. R's `ets()`
refuses seasonal periods above 24, and decomposing first (STL, then ETS) fails because STL needs more than two cycles.

| Model (test quarter) | MAE (£k/week) | RMSE | MAPE | WAPE | Bias |
|---|---|---|---|---|---|
| Naive | 134.8 | 146.2 | 47.2% | 49.6% | −49.6% |
| Seasonal naive (benchmark) | 42.7 | 52.9 | 18.0% | 15.7% | −4.5% |
| Fourier regression | **40.3** | **50.4** | **16.5%** | **14.8%** | −5.1% |
| Fourier + AR(1) errors | 40.3 | 50.5 | 16.5% | 14.8% | −5.1% |
| Prophet | **40.3** | **50.4** | **16.5%** | **14.8%** | −5.1% |

**Reading.**
- Seasonality is everything here: any model that knows last year's shape (seasonal naive or Fourier) cuts the error by about two-thirds compared with the naive forecast, which misses the autumn ramp-up completely.
- The Fourier regression beats the seasonal naive benchmark, but only slightly (WAPE 14.8% vs 15.7%; MAE about 6% lower). With only two years of history, a 10-term Fourier curve mostly reproduces last year's seasonal shape, smoothed. The extra modelling buys little accuracy over "same week last year".
- The AR(1) error term adds nothing: week-to-week deviations from the seasonal pattern are hardly autocorrelated (AR coefficient −0.17 on the full series), so Fourier regression and Fourier + AR(1) give almost identical forecasts.
- Prophet lands on practically the same forecasts as the Fourier regression (within £0.1k per week). This is expected: its yearly seasonality is the same 10-pair Fourier series, and with less than two years of data its changepoint mechanism finds no meaningful trend breaks. Prophet's convenience (holidays, changepoints) pays off with longer histories, not here.
- All models under-forecast the test quarter by about 5%: autumn 2011 ran slightly above autumn 2010.

**Next-quarter forecast** (Fourier + AR(1), refitted on all 104 weeks):

| Period | Forecast | Prophet | Seasonal naive |
|---|---|---|---|
| Dec 2011 (4 weeks from 5 Dec) | £601k | £605k | £581k |
| Jan 2012 (5 weeks from 2 Jan) | £733k | £726k | £677k |
| Feb 2012 (4 weeks from 6 Feb) | £554k | £553k | £508k |
| **Total, 13 weeks** | **£1,888k** | £1,883k | £1,766k |

Weekly 95% prediction intervals are about ±£50k. For the closed Christmas week the lower limit falls below zero and
should be read as zero.

**Hypothesis.** "A seasonal model beats a naive benchmark": **confirmed against the naive forecast; only marginally
against the seasonal naive benchmark.** For planning, the practical recommendation is to start from last year's
weekly profile and adjust it for the recent year-on-year trend; a more complex model becomes worthwhile once three
or more years of history are available.

### Part B: Repeat purchase within 90 days

**Design.** Out-of-time: the model is trained on customers active from Dec 2009 to Aug 2010 (outcome: a kept purchase
from 1 Sep to 29 Nov 2010) and tested on the same windows one year later.

| Set | Customers | Bought again within 90 days |
|---|---|---|
| Train (2010) | 3,287 | 58.4% |
| Test (2011) | 3,305 | 56.1% |

**Logistic regression** (odds ratio per one standard deviation, trained on 2010):

| Feature | Odds ratio | 95% CI | p-value | Reading |
|---|---|---|---|---|
| Frequency (purchase days) | **2.31** | 1.97–2.72 | <0.001 | The dominant driver |
| Variety (distinct products) | 1.22 | 1.09–1.35 | <0.001 | Broader buyers return more |
| Average order value | 1.13 | 1.03–1.23 | 0.009 | Slightly positive |
| Tenure | 0.88 | 0.78–0.99 | 0.028 | At equal frequency, newer customers are more active |
| Recency | 0.94 | 0.83–1.06 | 0.289 | Not significant once frequency is included |
| Cancellation share | 0.94 | 0.87–1.01 | 0.091 | Not significant |
| UK customer | 0.96 | 0.71–1.28 | 0.762 | No difference |

| Model (2011 test) | AUC | Gini | KS | Brier score |
|---|---|---|---|---|
| Logistic regression | 0.748 | 0.495 | 0.384 | 0.201 |
| Decision tree | 0.724 | 0.448 | 0.358 | 0.208 |
| Gradient boosting (XGBoost) | 0.740 | 0.479 | 0.372 | 0.204 |
| Always predicting the base rate | 0.500 | 0 | 0 | 0.246 |

Gradient boosting (300 trees of depth 3, learning rate 0.05, settings fixed in advance) does **not** beat logistic
regression on the 2011 test set (AUC 0.740 vs 0.748). The relationships are close to monotonic (more frequent, broader
buyers return more), which a linear model on log features already captures; the extra flexibility of boosting does not
generalise to the following year. Logistic regression is therefore the recommended model: it is also the easiest to
explain and to score in a spreadsheet. In the boosting model, frequency, recency and order value together carry about
76% of the total gain; variety 12%, cancellation share 6%, tenure 5% and UK 0%.

The decision tree uses the same signals: customers with more than about 2.5 purchase days who bought within the last
~110 days are classed as returning; customers with one or two purchase days are classed as returning only if they
bought a wide range of products (more than about 45).

**Gains (2011 test, ranked by the logistic score):**

| Decile | Customers | Bought again | Buy rate | Cumulative share of buyers |
|---|---|---|---|---|
| 1 (highest score) | 330 | 318 | 96% | 17% |
| 2 | 331 | 275 | 83% | 32% |
| 3 | 330 | 251 | 76% | 46% |
| 4–7 | 1,322 | 676 | 51% | 82% |
| 8–10 (lowest score) | 992 | 333 | 34% | 100% |

**Reading.**
- Hypothesis "recent and frequent customers are most likely to return": **frequency confirmed; recency is not significant on its own** once purchase frequency is known (frequent buyers are almost always recent too).
- The model ranks well and holds up one year later (AUC 0.75 on 2011 after training on 2010). The top 30% of customers by score buy again at 76–96%.
- For a retention budget: the top deciles will mostly return without help, so campaign spend is better aimed at the middle deciles (4–7, buy rate about 50%), where a nudge can change the outcome. The bottom deciles (about 30%) are lower priority. Whether a campaign actually changes behaviour must be tested with a controlled experiment (BQ8).

### Python–R reconciliation (BQ6)

| Result | Python | R | Largest difference |
|---|---|---|---|
| Naive, seasonal naive, Fourier regression accuracy | identical | identical | < 0.0001 |
| Fourier + AR(1) accuracy (`SARIMAX` vs `arima`) | MAE 40.31 | about 40.3 | 0.047 |
| Logistic odds ratios | identical | identical | 3.5 × 10⁻⁵ |
| Logistic AUC / tree AUC | 0.7476 / 0.7240 | 0.7476 / 0.7240 | 0 |
| Prophet accuracy | MAE 40.27 | MAE 40.27 | < 0.0001 |
| Gradient boosting AUC (XGBoost) | 0.7396 | 0.7396 | 0 |
| Gains table, buyers per decile | identical | identical | 0 |

The ARIMA-error model is estimated by numerical maximum likelihood with different optimisers in statsmodels and R,
so small differences are expected; the regression benchmarks and the logistic model are closed-form or converge to
the same solution and agree exactly. Prophet (Stan) and XGBoost run the same underlying libraries in both languages;
with deterministic settings (exact tree method, no sampling, one thread) they agree to four decimals.

**Limitations.** Two years of weekly data (two Christmas seasons) limit any forecasting model; AIC chose the largest
K tested, a sign that the seasonal shape is learned largely from a single previous year. The repeat-purchase model
uses only transaction history (no marketing contacts or website behaviour).
