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