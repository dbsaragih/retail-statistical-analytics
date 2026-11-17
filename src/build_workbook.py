"""Build the client workbook for retail-statistical-analytics (stage 18).

Reads reports/dashboard_data/*.csv and writes the full client workbook (14 sheets). The full version is kept
in private/ (git-ignored); reports/deliverables/ holds a public preview (Summary and BQ1–BQ3).

Usage (WSL):
    ~/venvs/stats/bin/python src/build_workbook.py reports/dashboard_data private/retail_analytics_client_workbook.xlsx

Formulas are written without cached values; Excel calculates them on opening.
"""
import sys
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.comments import Comment

DASH = Path(sys.argv[1])
OUT = Path(sys.argv[2])

FONT = "Aptos Narrow"
INK, QUIET = "1F2933", "52606D"
BLUE, ORANGE, GREEN, GREY = "64B5F6", "FF8A65", "81C784", "BDBDBD"
HEAD_FILL = PatternFill("solid", fgColor="DCE9F5")
TITLE_FILL = PatternFill("solid", fgColor="EEF4FA")
INPUT_FILL = PatternFill("solid", fgColor="FFF59D")
THIN = Side(style="thin", color="C9D3DD")
BOX = Border(top=THIN, bottom=THIN, left=THIN, right=THIN)

GBP = '£#,##0;-£#,##0;"-"'
GBP2 = '£#,##0.00'
GBPK = '£#,##0.0"k"'
PCT = '0.0%'
INT = '#,##0'
DEC2, DEC3 = '0.00', '0.000'
PVAL = '[<0.001]"< 0.001";0.000'
DATE = 'dd mmm yyyy'
MONTH = 'mmm yyyy'

def f(size=11, bold=False, color=INK, italic=False):
    return Font(name=FONT, size=size, bold=bold, color=color, italic=italic)

def read(name, **kw):
    return pd.read_csv(DASH / f"{name}.csv", **kw)

wb = Workbook()
wb.remove(wb.active)

def sheet(name, title, subtitle, widths=None):
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False
    ws["A1"] = title; ws["A1"].font = f(16, True)
    ws["A2"] = subtitle; ws["A2"].font = f(11, color=QUIET, italic=True)
    for col, w in (widths or {}).items():
        ws.column_dimensions[col].width = w
    ws["A3"] = '=HYPERLINK("#\'README\'!A1","← Back to README")'
    ws["A3"].font = f(10, color="1565C0")
    return ws

def heading(ws, row, text, col=1):
    c = ws.cell(row=row, column=col, value=text)
    c.font = f(13, True)
    return row + 1

def note(ws, row, text, col=1):
    c = ws.cell(row=row, column=col, value=text)
    c.font = f(10, color=QUIET, italic=True)
    return row + 1

def table(ws, df, row, col=1, fmts=None, name=None, headers=None):
    """Write df at (row, col) as an Excel table. Returns (first_data_row, last_data_row)."""
    fmts = fmts or {}
    heads = headers or list(df.columns)
    for j, h in enumerate(heads):
        c = ws.cell(row=row, column=col + j, value=h)
        c.font = f(11, True); c.fill = HEAD_FILL; c.border = BOX
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for i, rec in enumerate(df.itertuples(index=False), start=1):
        for j, v in enumerate(rec):
            if isinstance(v, float) and pd.isna(v):
                v = None
            c = ws.cell(row=row + i, column=col + j, value=v)
            c.font = f(); c.border = BOX
            key = df.columns[j]
            if key in fmts:
                c.number_format = fmts[key]
    last = row + len(df)
    if name:
        ref = f"{get_column_letter(col)}{row}:{get_column_letter(col + len(heads) - 1)}{last}"
        t = Table(displayName=name, ref=ref)
        t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
        ws.add_table(t)
    return row + 1, last

def style_chart(ch, title, ytitle=None, xtitle=None, w=16, h=8):
    ch.title = title
    ch.roundedCorners = False
    ch.width, ch.height = w, h
    if ytitle: ch.y_axis.title = ytitle
    if xtitle: ch.x_axis.title = xtitle
    if hasattr(ch, "x_axis"):
        ch.x_axis.delete = False; ch.y_axis.delete = False
    if ch.legend is not None:
        ch.legend.overlay = False; ch.legend.position = "b"
    return ch

def color_series(ch, colors, line=False):
    for s, colr in zip(ch.series, colors):
        if line:
            s.graphicalProperties.line.solidFill = colr
            s.graphicalProperties.line.width = 22000
            s.smooth = False
        else:
            s.graphicalProperties.solidFill = colr
            s.graphicalProperties.line.solidFill = colr

# ------------------------------------------------------------------ data
mk = read("monthly_kpis", parse_dates=["month"])
wk = read("weekday_pattern"); hr = read("hour_pattern")
vd = read("value_drivers"); co = read("cancellation_odds"); cp = read("cancellation_model_performance")
seg = read("customer_rfm_segments"); clu = read("customer_clusters"); abc = read("product_abc")
pcl = read("product_clusters"); rfm = read("customer_rfm")
top = read("basket_top_products"); pairs = read("basket_pairs"); rules = read("basket_rules")
fa = read("forecast_accuracy"); fq = read("forecast_next_quarter", parse_dates=["week"])
fw = read("forecast_weekly", parse_dates=["week"])
rg = read("repeat_gains"); ro = read("repeat_odds"); rp = read("repeat_performance")
ad = read("anomaly_days", parse_dates=["date"]); ap = read("anomaly_profile")
ai = read("anomaly_invoices_top", parse_dates=["date"])
ht = read("hypothesis_tests"); bi = read("bootstrap_intervals"); ab = read("ab_sample_size")

LABEL = {"recency": "Days since last purchase", "frequency": "Purchase frequency", "order_value": "Average order value",
         "variety": "Product variety", "tenure": "Tenure", "cancel_share": "Cancellation share", "is_uk": "UK customer",
         "log_qty": "Quantity (log)", "log_price": "Unit price (log)", "log_basket": "Basket size (log)",
         "log_prior_orders": "Prior orders (log)", "q4": "Q4 (Oct–Dec)", "late_hour": "Late hour (16:00+)",
         "is_price_outlier": "Price outlier (>5× or <0.2× normal)"}
CLUSTER_NAMES = {1: "VIP regulars", 2: "Mid-value, cooling", 3: "Recent newcomers", 4: "Lapsed one-timers"}
MODEL_NAMES = {"naive": "Naive (last week)", "seasonal_naive": "Same week last year (benchmark)",
               "fourier_ols": "Fourier regression", "fourier_ar1": "Fourier + AR(1) errors", "prophet": "Prophet"}

# ================================================================ README
ws = wb.create_sheet("README"); ws.sheet_view.showGridLines = False
ws.column_dimensions["A"].width = 26; ws.column_dimensions["B"].width = 100
ws["A1"] = "Retail Statistical Analytics: client workbook"; ws["A1"].font = f(18, True)
ws["A2"] = "UK online giftware wholesaler · two years of transactions (Dec 2009 – Nov 2011) · eight business questions"
ws["A2"].font = f(11, color=QUIET, italic=True)
r = 4
info = [
    ("Purpose", "The key results of the analysis in one file: answers, recommendations and the tables behind them, with native Excel charts."),
    ("Data", "Chen, D. (2012). Online Retail II. UCI Machine Learning Repository, https://doi.org/10.24432/C5CG6D. Licence: CC BY 4.0."),
    ("Year 1 / Year 2", "Year 1 = 1 Dec 2009 – 30 Nov 2010; Year 2 = 1 Dec 2010 – 30 Nov 2011."),
    ("Net revenue", "Gross product sales minus cancellations of product lines; postage, fees and manual adjustments excluded. GBP."),
    ("Method", "Every result was computed twice, in Python and in R, and the two were reconciled (see docs/04_reconciliation.md)."),
    ("How to read", "Tables are values exported by the analysis notebooks; totals, shares and comparisons are live Excel formulas. "
                    "Yellow cells on the BQ8 sheet are inputs you can change (A/B test calculator)."),
    ("Limitations", "Two years of history; no costs or margins; no marketing or web data; group differences are associations, not causes."),
    ("Interactive version", "Looker Studio dashboard: https://datastudio.google.com/reporting/f4108bc3-ed9f-4531-ad69-5212a8e33b36"),
]
for k, v in info:
    ws.cell(row=r, column=1, value=k).font = f(11, True)
    c = ws.cell(row=r, column=2, value=v); c.font = f(); c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.cell(row=r, column=1).alignment = Alignment(vertical="top")
    r += 1
r += 1
ws.cell(row=r, column=1, value="Sheets").font = f(13, True); r += 1
index = [("Summary", "Answers to BQ1–BQ8, headline numbers, recommendations"),
         ("BQ1 Trend", "Monthly revenue, orders and customers; Year 2 vs Year 1"),
         ("BQ2 Seasonality", "Sales by weekday and by hour"),
         ("BQ3 Drivers", "What predicts customer value; what drives cancellations"),
         ("BQ4 Segments", "RFM segments, customer clusters, ABC product classes, product clusters"),
         ("BQ5 Baskets", "Most frequent products; product pairs bought together"),
         ("BQ6 Forecast", "Next-quarter forecast, model accuracy, repeat-purchase gains"),
         ("BQ7 Anomalies", "Unusual days and unusual invoices"),
         ("BQ8 Tests", "Hypothesis tests, bootstrap intervals, A/B test sample-size calculator"),
         ("Data_Customers", "One row per Year 2 customer: RFM scores, segment, cluster (filterable)"),
         ("Data_Rules", "All 1,488 association rules"),
         ("Data_Anomalies", "All 393 flagged invoices"),
         ("Dictionary", "Definitions of every column")]
for name, desc in index:
    c = ws.cell(row=r, column=1, value=f'=HYPERLINK("#\'{name}\'!A1","{name}")'); c.font = f(11, color="1565C0")
    ws.cell(row=r, column=2, value=desc).font = f()
    r += 1

# ================================================================ BQ1
ws = sheet("BQ1 Trend", "BQ1 · How is the business trending?",
           "Monthly totals; Year 2 compared with the same months of Year 1",
           {"A": 12, "B": 14, "C": 14, "D": 14, "E": 10, "F": 11, "G": 13, "H": 11, "I": 3,
            "J": 12, "K": 14, "L": 14, "M": 11})
r = heading(ws, 5, "Monthly KPIs")
m = mk.copy()
m["year"] = ["Year 1"] * 12 + ["Year 2"] * 12
m = m[["month", "year", "net_revenue", "gross_sales", "cancellations", "orders", "customers", "avg_order_value", "cancel_rate"]]
first, last = table(ws, m, r, 1, {"month": MONTH, "net_revenue": GBP, "gross_sales": GBP, "cancellations": GBP,
                                  "orders": INT, "customers": INT, "avg_order_value": GBP2, "cancel_rate": PCT},
                    headers=["Month", "Year", "Net revenue", "Gross sales", "Cancellations", "Orders", "Customers",
                             "Value per order", "Cancel rate"])
MK_FIRST, MK_LAST = first, last
# Year comparison block (formulas)
r2 = heading(ws, 5, "Year 2 vs Year 1", col=10)
for j, h in enumerate(["Measure", "Year 1", "Year 2", "Change"]):
    c = ws.cell(row=r2, column=10 + j, value=h); c.font = f(11, True); c.fill = HEAD_FILL; c.border = BOX
yr = f"$B${first}:$B${last}"
rows = [("Net revenue", "C", GBP), ("Orders", "F", INT)]
rr = r2 + 1
for label, colL, fmt in rows:
    ws.cell(row=rr, column=10, value=label)
    ws.cell(row=rr, column=11, value=f'=SUMIFS(${colL}${first}:${colL}${last},{yr},"Year 1")').number_format = fmt
    ws.cell(row=rr, column=12, value=f'=SUMIFS(${colL}${first}:${colL}${last},{yr},"Year 2")').number_format = fmt
    ws.cell(row=rr, column=13, value=f"=L{rr}/K{rr}-1").number_format = '+0.0%;-0.0%'
    rr += 1
ws.cell(row=rr, column=10, value="Value per order")
ws.cell(row=rr, column=11, value=f"=K{r2+1}/K{r2+2}").number_format = GBP2
ws.cell(row=rr, column=12, value=f"=L{r2+1}/L{r2+2}").number_format = GBP2
ws.cell(row=rr, column=13, value=f"=L{rr}/K{rr}-1").number_format = '+0.0%;-0.0%'
YR_NET_ROW, YR_ORD_ROW, YR_AOV_ROW = r2 + 1, r2 + 2, rr
for row_ in range(r2 + 1, rr + 1):
    for col_ in range(10, 14):
        ws.cell(row=row_, column=col_).font = f(); ws.cell(row=row_, column=col_).border = BOX
rr += 1
rr = note(ws, rr, "Customers are not summed across months (one customer buys in many months).", 10)
rr = note(ws, rr, "Value per order here = total net revenue ÷ orders (+6.1%); docs/03_findings.md reports +5.9% from notebook 02.", 10)
rr = note(ws, rr, "Trend test with month controls: +2.1% a year, p = 0.52 (not significant). Source: notebook 02.", 10)

# side-by-side months for the chart
cr = rr + 1
heading(ws, cr, "Net revenue by month, Year 1 vs Year 2", col=10)
for j, h in enumerate(["Month", "Year 1", "Year 2"]):
    c = ws.cell(row=cr + 1, column=10 + j, value=h); c.font = f(11, True); c.fill = HEAD_FILL; c.border = BOX
for i in range(12):
    row_ = cr + 2 + i
    ws.cell(row=row_, column=10, value=f'=TEXT(A{first + 12 + i},"mmm")')
    ws.cell(row=row_, column=11, value=f"=C{first + i}").number_format = GBP
    ws.cell(row=row_, column=12, value=f"=C{first + 12 + i}").number_format = GBP
    for col_ in range(10, 13):
        ws.cell(row=row_, column=col_).font = f(); ws.cell(row=row_, column=col_).border = BOX
ch = LineChart()
ch.add_data(Reference(ws, min_col=11, max_col=12, min_row=cr + 1, max_row=cr + 13), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=10, min_row=cr + 2, max_row=cr + 13))
style_chart(ch, "Net revenue by month (£)", None, None, 18, 8)
color_series(ch, [GREY, BLUE], line=True)
ch.y_axis.numFmt = '£#,##0'
ws.add_chart(ch, f"J{cr + 15}")

# ================================================================ BQ2
ws = sheet("BQ2 Seasonality", "BQ2 · When do customers buy?",
           "Sales per trading day by weekday (closed on Saturdays) and share of sales by hour",
           {"A": 14, "B": 18, "C": 14, "D": 3, "E": 10, "F": 16})
r = heading(ws, 5, "By weekday")
w = wk.copy()
first, last = table(ws, w, r, 1, {"sales_per_trading_day": GBP}, headers=["Weekday", "Sales per trading day", "vs average"])
for i in range(first, last + 1):
    c = ws.cell(row=i, column=3, value=f"=B{i}/AVERAGE($B${first}:$B${last})-1"); c.number_format = '+0%;-0%'; c.font = f(); c.border = BOX
ch = BarChart(); ch.type = "col"
ch.add_data(Reference(ws, min_col=2, min_row=r, max_row=last), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=first, max_row=last))
style_chart(ch, "Sales per trading day (£)", w=14, h=7); ch.legend = None
color_series(ch, [BLUE]); ch.y_axis.numFmt = '£#,##0'
ws.add_chart(ch, "H21")
r = heading(ws, 5, "By hour", col=5)
first, last = table(ws, hr, r, 5, {"share_of_sales": PCT}, headers=["Hour", "Share of sales"])
ws.cell(row=last + 1, column=5, value="Total").font = f(11, True)
c = ws.cell(row=last + 1, column=6, value=f"=SUM(F{first}:F{last})"); c.number_format = PCT; c.font = f(11, True)
ws.cell(row=last + 2, column=5, value="10:00–15:00").font = f()
c = ws.cell(row=last + 2, column=6, value=f'=SUMIFS(F{first}:F{last},E{first}:E{last},">=10",E{first}:E{last},"<=15")')
c.number_format = PCT; c.font = f()
ch = BarChart(); ch.type = "col"
ch.add_data(Reference(ws, min_col=6, min_row=r, max_row=last), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=5, min_row=first, max_row=last))
style_chart(ch, "Share of sales by hour", w=14, h=7); ch.legend = None
color_series(ch, [ORANGE]); ch.y_axis.numFmt = '0%'
ws.add_chart(ch, "H5")
note(ws, 30, "Sep–Nov brings 36–38% of annual revenue; November alone about 15% (see BQ1 monthly table).")

# ================================================================ BQ3
ws = sheet("BQ3 Drivers", "BQ3 · What drives customer value and cancellations?",
           "Part A: Year 1 behaviour → Year 2 value (OLS, HC3 errors). Part B: cancellation risk per order line (logistic regression).",
           {"A": 32, "B": 14, "C": 12, "D": 12, "E": 12, "F": 3, "G": 38, "H": 12, "I": 10, "J": 10, "K": 10})
r = heading(ws, 5, "A. Drivers of Year 2 customer value (per 1 SD in Year 1)")
v = vd.assign(driver=vd["driver"].map(LABEL))[["driver", "effect_per_sd", "coef", "robust_se", "p_value"]]
v = v.sort_values("effect_per_sd", ascending=False)
first, last = table(ws, v, r, 1, {"effect_per_sd": '+0%;-0%', "coef": DEC3, "robust_se": DEC3, "p_value": PVAL},
                    headers=["Driver", "Effect on Year 2 value", "Coefficient", "Robust SE", "p-value"])
ws.cell(row=last + 1, column=1, value="R² = 0.347 · 4,227 customers. Effect = exp(coef) − 1 on (1 + Year 2 revenue).").font = f(10, color=QUIET, italic=True)
ch = BarChart(); ch.type = "bar"
ch.add_data(Reference(ws, min_col=2, min_row=r, max_row=last), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=first, max_row=last))
style_chart(ch, "Effect on Year 2 value per 1 SD", w=15, h=7.5); ch.legend = None
color_series(ch, [BLUE]); ch.y_axis.numFmt = '0%'; ch.x_axis.scaling.orientation = "maxMin"
ch.x_axis.tickLblPos = "low"
ws.add_chart(ch, f"A{last + 4}")
r = heading(ws, 5, "B. Cancellation risk: odds ratios", col=7)
o = co.assign(feature=co["feature"].map(LABEL))[["feature", "odds_ratio", "ci_low", "ci_high", "p_value"]]
o = o.sort_values("odds_ratio", ascending=False)
first, last = table(ws, o, r, 7, {"odds_ratio": DEC2, "ci_low": DEC2, "ci_high": DEC2, "p_value": PVAL},
                    headers=["Factor", "Odds ratio", "CI low", "CI high", "p-value"])
ws.cell(row=last + 1, column=7, value="Odds ratio > 1 = more likely to be cancelled. Trained on Year 1, tested on Year 2.").font = f(10, color=QUIET, italic=True)
r = heading(ws, last + 3, "Model performance (Year 2 test)", col=7)
first, last = table(ws, cp, r, 7, {"auc": DEC3, "gini": DEC3, "ks": DEC3}, headers=["Model", "AUC", "Gini", "KS"])

# ================================================================ BQ4
ws = sheet("BQ4 Segments", "BQ4 · Which customer and product segments exist?",
           "Year 2 (Dec 2010 – Nov 2011). Shares are live formulas from the counts and revenue.",
           {"A": 22, "B": 11, "C": 11, "D": 14, "E": 11, "F": 12, "G": 12, "H": 13, "I": 3,
            "J": 22, "K": 11, "L": 11, "M": 14, "N": 11})
def seg_table(ws, df, r, col, label_col, label_head, count_head):
    d = df.copy()
    d = d[[label_col, d.columns[1], d.columns[3], "median_recency", "median_frequency", "median_monetary"]] if "median_recency" in d else d
    return d

r = heading(ws, 5, "RFM segments (rules on recency and frequency scores)")
s = seg[["rfm_segment", "customers", "revenue", "median_recency", "median_frequency", "median_monetary"]].copy()
s.insert(2, "customer_share", None); s.insert(4, "revenue_share", None)
first, last = table(ws, s, r, 1, {"customers": INT, "revenue": GBP, "median_recency": INT, "median_frequency": INT,
                                  "median_monetary": GBP},
                    headers=["Segment", "Customers", "Share of customers", "Net revenue", "Share of revenue",
                             "Median days since last", "Median purchase days", "Median net revenue"])
for i in range(first, last + 1):
    ws.cell(row=i, column=3, value=f"=B{i}/SUM($B${first}:$B${last})").number_format = '0%'
    ws.cell(row=i, column=5, value=f"=D{i}/SUM($D${first}:$D${last})").number_format = '0%'
ws.cell(row=last + 1, column=1, value="Total").font = f(11, True)
for colL, fmt in [("B", INT), ("D", GBP)]:
    c = ws[f"{colL}{last + 1}"]; c.value = f"=SUM({colL}{first}:{colL}{last})"; c.number_format = fmt; c.font = f(11, True)
SEG_FIRST, SEG_LAST = first, last
ch = BarChart(); ch.type = "col"; ch.grouping = "clustered"
ch.add_data(Reference(ws, min_col=3, min_row=r, max_row=last), titles_from_data=True)
ch.add_data(Reference(ws, min_col=5, min_row=r, max_row=last), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=first, max_row=last))
style_chart(ch, "Share of customers vs share of revenue", w=16, h=7.5)
color_series(ch, [GREY, BLUE]); ch.y_axis.numFmt = '0%'
ws.add_chart(ch, f"A{last + 3}")

r = heading(ws, 5, "Customer clusters (k-means, k = 4)", col=10)
c4 = clu.assign(name=clu["cluster"].map(CLUSTER_NAMES))[["cluster", "name", "customers", "revenue", "median_recency",
                                                         "median_frequency", "median_monetary"]]
c4.insert(3, "customer_share", None); c4.insert(5, "revenue_share", None)
first, last = table(ws, c4, r, 10, {"customers": INT, "revenue": GBP, "median_recency": '0', "median_frequency": INT,
                                    "median_monetary": GBP},
                    headers=["Cluster", "Name", "Customers", "Share of customers", "Net revenue", "Share of revenue",
                             "Median days since last", "Median purchase days", "Median net revenue"])
for i in range(first, last + 1):
    ws.cell(row=i, column=13, value=f"=L{i}/SUM($L${first}:$L${last})").number_format = '0%'
    ws.cell(row=i, column=15, value=f"=N{i}/SUM($N${first}:$N${last})").number_format = '0%'
for col_ in "OPQR":
    ws.column_dimensions[col_].width = 12
ws.column_dimensions["K"].width = 20
note(ws, last + 1, "Cluster 2 holds 421 of the 667 'At risk' customers: the main win-back target.", 10)

r = heading(ws, 30, "ABC product classes (A = first 80% of revenue)", col=10)
a = abc[["abc", "products", "revenue", "median_price", "median_customers"]].copy()
a.insert(2, "product_share", None); a.insert(4, "revenue_share", None)
first, last = table(ws, a, r, 10, {"products": INT, "revenue": GBP, "median_price": GBP2, "median_customers": INT},
                    headers=["Class", "Products", "Share of products", "Net revenue", "Share of revenue",
                             "Median price", "Median customers"])
for i in range(first, last + 1):
    ws.cell(row=i, column=12, value=f"=K{i}/SUM($K${first}:$K${last})").number_format = '0%'
    ws.cell(row=i, column=14, value=f"=M{i}/SUM($M${first}:$M${last})").number_format = '0%'

r = heading(ws, last + 3, "Product clusters (products with 20+ orders)", col=10)
p = pcl[["cluster", "products", "revenue", "median_price", "mean_q4_share", "share_class_A"]]
first, last = table(ws, p, r, 10, {"products": INT, "revenue": GBP, "median_price": GBP2, "mean_q4_share": '0%',
                                   "share_class_A": '0%'},
                    headers=["Cluster", "Products", "Net revenue", "Median price", "Avg Q4 share", "Share in class A"])
note(ws, last + 1, "Cluster 2 = seasonal (Christmas) lines: 75% of their sales in Q4.", 10)

# ================================================================ BQ5
ws = sheet("BQ5 Baskets", "BQ5 · Which products are bought together?",
           "18,837 Year 2 baskets. Support = share of baskets; confidence = P(B | A); lift = how many times more likely than chance.",
           {"A": 44, "B": 44, "C": 11, "D": 10, "E": 10, "F": 10})
r = heading(ws, 5, "Most frequent products")
first, last = table(ws, top[["product", "stock_code", "support"]], r, 1, {"support": PCT},
                    headers=["Product", "Stock code", "Share of baskets"])
pp = pairs.copy()
cols = ["product_a", "product_b", "support", "conf_a_to_b", "conf_b_to_a", "lift"]
heads = ["Product A", "Product B", "Baskets with both", "A → B", "B → A", "Lift"]
fm = {"support": PCT, "conf_a_to_b": '0%', "conf_b_to_a": '0%', "lift": '0.0'}
r = heading(ws, last + 3, "Strongest links: top 20 pairs by lift")
first, last = table(ws, pp.sort_values(["lift", "product_a"], ascending=[False, True]).head(20)[cols], r, 1, fm, headers=heads)
r = heading(ws, last + 3, "Most common combinations: top 20 pairs by support")
first, last = table(ws, pp.sort_values(["support", "product_a"], ascending=[False, True]).head(20)[cols], r, 1, fm, headers=heads)
note(ws, last + 1, "All 1,488 rules are on the Data_Rules sheet. Confidence is not symmetric: the higher direction marks the anchor product.")
note(ws, last + 2, "A blank confidence means no rule in that direction (confidence below the 30% threshold).")

# ================================================================ BQ6
ws = sheet("BQ6 Forecast", "BQ6 · What will revenue be next quarter, and who will buy again?",
           "Weekly net revenue in £ thousand. Test quarter = 5 Sep – 28 Nov 2011; next quarter = 5 Dec 2011 – 27 Feb 2012.",
           {"A": 13, "B": 12, "C": 11, "D": 11, "E": 13, "F": 11, "G": 3, "H": 30, "I": 11, "J": 11, "K": 11, "L": 11, "M": 11})
r = heading(ws, 5, "Next-quarter forecast (Fourier + AR(1), £k per week)")
q = fq[["week", "forecast", "lo95", "hi95", "prophet", "seasonal_naive"]]
first, last = table(ws, q, r, 1, {"week": DATE, "forecast": '0.0', "lo95": '0.0', "hi95": '0.0', "prophet": '0.0',
                                  "seasonal_naive": '0.0'},
                    headers=["Week", "Forecast", "Lower 95%", "Upper 95%", "Prophet", "Same week last year"])
ws.cell(row=last + 1, column=1, value="Total 13 weeks").font = f(11, True)
for colL in "BEF":
    c = ws[f"{colL}{last + 1}"]; c.value = f"=SUM({colL}{first}:{colL}{last})"; c.number_format = GBPK; c.font = f(11, True)
FQ_TOTAL = f"B{last + 1}"
rr = last + 2
for mon, lo, hi in [("Dec 2011", "2011-12-01", "2011-12-31"), ("Jan 2012", "2012-01-01", "2012-01-31"),
                    ("Feb 2012", "2012-02-01", "2012-02-29")]:
    ws.cell(row=rr, column=1, value=mon).font = f()
    for colL in "BEF":
        c = ws[f"{colL}{rr}"]
        y, mth = int(lo[:4]), int(lo[5:7])
        c.value = (f'=SUMIFS({colL}{first}:{colL}{last},$A${first}:$A${last},">="&DATE({y},{mth},1),'
                   f'$A${first}:$A${last},"<"&DATE({y},{mth}+1,1))')
        c.number_format = GBPK; c.font = f()
    rr += 1
note(ws, rr, "Weeks are counted in the month of their Monday. The closed Christmas week's lower limit is below zero: read it as zero.")
ch = LineChart()
ch.add_data(Reference(ws, min_col=2, max_col=4, min_row=r, max_row=last), titles_from_data=True)
ch.add_data(Reference(ws, min_col=6, min_row=r, max_row=last), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=first, max_row=last))
style_chart(ch, "Next quarter: weekly forecast with 95% interval (£k)", w=13.5, h=8)
color_series(ch, [ORANGE, GREY, GREY, BLUE], line=True)
ch.x_axis.number_format = 'dd mmm'
ws.add_chart(ch, f"A{rr + 6}")

r = heading(ws, 5, "Forecast accuracy on the test quarter", col=8)
acc = fa.assign(model=fa["model"].map(MODEL_NAMES)).sort_values("WAPE")
acc[["MAPE", "WAPE", "bias_pct"]] = acc[["MAPE", "WAPE", "bias_pct"]] / 100
first, last = table(ws, acc, r, 8, {"MAE": '0.0', "RMSE": '0.0', "MAPE": PCT, "WAPE": PCT, "bias_pct": '+0.0%;-0.0%'},
                    headers=["Model", "MAE (£k)", "RMSE (£k)", "MAPE", "WAPE", "Bias"])
rr = last + 1
ws.cell(row=rr, column=8, value="Best model vs benchmark (WAPE)").font = f(11, True)
c = ws.cell(row=rr, column=12,
            value=f'=MIN(L{first}:L{last})-INDEX(L{first}:L{last},MATCH("Same week last year (benchmark)",H{first}:H{last},0))')
c.number_format = '+0.0" pts";-0.0" pts"'; c.font = f(11, True)
c.comment = Comment("Percentage points of WAPE. Negative = the best model is more accurate than the benchmark.", "analysis")
for col_ in range(9, 14):
    ws.cell(row=r, column=col_).alignment = Alignment(horizontal="center", wrap_text=True)

r = heading(ws, last + 4, "Repeat purchase within 90 days: gains by score decile (2011 test)", col=8)
g = rg[["decile", "customers", "buyers", "mean_score"]].copy()
first, last = table(ws, g, r, 8, {"customers": INT, "buyers": INT, "mean_score": DEC3},
                    headers=["Decile (1 = highest)", "Customers", "Bought again", "Mean score", "Buy rate",
                             "Cumulative share of buyers", "Lift vs average"])
for col_, h in zip(range(12, 15), ["Buy rate", "Cumulative share of buyers", "Lift vs average"]):
    c = ws.cell(row=r, column=col_, value=h); c.font = f(11, True); c.fill = HEAD_FILL; c.border = BOX
    c.alignment = Alignment(horizontal="center", wrap_text=True)
for i in range(first, last + 1):
    ws.cell(row=i, column=12, value=f"=J{i}/I{i}").number_format = '0%'
    ws.cell(row=i, column=13, value=f"=SUM($J${first}:J{i})/SUM($J${first}:$J${last})").number_format = '0%'
    ws.cell(row=i, column=14, value=f"=L{i}/(SUM($J${first}:$J${last})/SUM($I${first}:$I${last}))").number_format = '0.00'
    for col_ in range(12, 15):
        ws.cell(row=i, column=col_).font = f(); ws.cell(row=i, column=col_).border = BOX
ws.column_dimensions["N"].width = 11
ch = BarChart(); ch.type = "col"
ch.add_data(Reference(ws, min_col=12, min_row=r, max_row=last), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=8, min_row=first, max_row=last))
style_chart(ch, "Buy rate by score decile", w=15, h=7)
color_series(ch, [BLUE]); ch.y_axis.numFmt = '0%'; ch.legend = None
ws.add_chart(ch, f"P{r}")
r = heading(ws, last + 3, "What predicts a repeat purchase (odds ratio per 1 SD)", col=8)
o = ro.assign(feature=ro["feature"].map(LABEL)).sort_values("odds_ratio", ascending=False)
first, last = table(ws, o, r, 8, {"odds_ratio": DEC2, "ci_low": DEC2, "ci_high": DEC2, "p_value": PVAL},
                    headers=["Feature", "Odds ratio", "CI low", "CI high", "p-value"])
r = heading(ws, last + 2, "Model performance (2011 test)", col=8)
table(ws, rp, r, 8, {"auc": DEC3, "gini": DEC3, "ks": DEC3, "brier": DEC3}, headers=["Model", "AUC", "Gini", "KS", "Brier"])

# ================================================================ BQ7
ws = sheet("BQ7 Anomalies", "BQ7 · Which days and invoices are unusual?",
           "Days: deviation from expected level (weekday + month), flagged by z-score, control chart (±2.66 × average moving range) and IQR. Invoices: Isolation Forest, top 1%.",
           {"A": 13, "B": 12, "C": 13, "D": 13, "E": 11, "F": 10, "G": 9, "H": 9, "I": 9, "J": 3})
r = heading(ws, 5, "The 7 flagged days")
d = ad[["date", "weekday", "net", "expected", "resid", "flag_z", "flag_chart", "flag_iqr"]].copy()
d.insert(5, "deviation_pct", None)
for k in ["flag_z", "flag_chart", "flag_iqr"]:
    d[k] = d[k].map({True: "Yes", False: "–"})
first, last = table(ws, d, r, 1, {"date": DATE, "net": GBP, "expected": GBP, "resid": DEC2},
                    headers=["Date", "Weekday", "Net revenue", "Expected", "Deviation (log)", "Deviation (%)",
                             "z-rule", "Chart", "IQR"])
for i in range(first, last + 1):
    c = ws.cell(row=i, column=6, value=f"=C{i}/D{i}-1"); c.number_format = '+0%;-0%'; c.font = f(); c.border = BOX
note(ws, last + 1, "Most have calendar explanations (Christmas wind-down, New Year restart, quiet Sundays); 27 Sep 2010 is the one real spike.")
r = heading(ws, last + 3, "Flagged invoices (top 1%) vs all others")
pr = ap.set_index("group").T.reset_index()
pr.columns = ["measure", "flagged", "others"]
names = {"invoices": "Invoices", "median_value": "Median value", "median_lines": "Median lines",
         "has_nonproduct": "Has a non-product line", "has_cancelled": "Has a cancelled line",
         "has_bulk_line": "Has a bulk line (500+)", "has_price_outlier": "Has a price outlier",
         "no_customer": "No customer ID", "non_uk": "Non-UK customer"}
pr["measure"] = pr["measure"].map(names)
first, last = table(ws, pr, r, 1, {}, headers=["Measure", "Flagged (top 1%)", "All other invoices"])
for i, key in zip(range(first, last + 1), ap.columns[1:]):
    fmt = INT if key in ("invoices", "median_lines") else (GBP if key == "median_value" else '0.0%')
    for col_ in (2, 3):
        ws.cell(row=i, column=col_).number_format = fmt
ws.column_dimensions["A"].width = 24
note(ws, last + 1, "Unusual invoices are single manual non-product entries, often non-UK or unidentified and later reversed; large orders are routine.")
r = heading(ws, 5, "Top 25 most anomalous invoices", col=11)
inv = ai.sort_values("score", ascending=False).head(25)[["invoice", "date", "lines", "value", "nonproduct_share",
                                                         "cancelled_share", "has_customer", "is_uk", "score"]].copy()
inv["invoice"] = inv["invoice"].astype(str)
for k in ["has_customer", "is_uk"]:
    inv[k] = inv[k].map({True: "Yes", False: "No"})
table(ws, inv, r, 11, {"date": DATE, "lines": INT, "value": GBP, "nonproduct_share": '0%', "cancelled_share": '0%', "score": DEC3},
      headers=["Invoice", "Date", "Lines", "Value", "Non-product share", "Cancelled share", "Customer ID", "UK", "Score"])
for col_, wdt in zip("KLMNOPQRS", [10, 12, 7, 11, 11, 11, 10, 7, 8]):
    ws.column_dimensions[col_].width = wdt

# ================================================================ BQ8
ws = sheet("BQ8 Tests", "BQ8 · Are the differences real, and how should a campaign be tested?",
           "Part A: tests on observed groups (associations, not causes). Part B: sample size for a win-back email A/B test.",
           {"A": 40, "B": 26, "C": 14, "D": 12, "E": 26, "F": 13, "G": 13})
r = heading(ws, 5, "A. Hypothesis tests (Year 2)")
h = ht.copy()
for k in ["significant_0.05", "significant_bonferroni"]:
    h[k] = h[k].map({True: "Yes", False: "No"})
first, last = table(ws, h, r, 1, {"statistic": '#,##0.0', "p_value": PVAL},
                    headers=["Comparison", "Test", "Statistic", "p-value", "Effect size", "Significant (5%)",
                             "Significant (Bonferroni)"])
for i in range(first, last + 1):
    for col_ in (4, 6, 7):
        ws.cell(row=i, column=col_).alignment = Alignment(horizontal="center")
note(ws, last + 1, "Bonferroni threshold = 0.05 / 4 = 0.0125. With tens of thousands of observations significance is easy; the effect size shows what matters.")
r = heading(ws, last + 3, "Bootstrap 95% intervals: non-UK minus UK order value (2,000 resamples)")
first, last = table(ws, bi, r, 1, {"estimate": GBP, "ci_low": GBP, "ci_high": GBP},
                    headers=["Statistic", "Estimate", "95% CI low", "95% CI high"])

r = heading(ws, last + 3, "B. A/B test calculator: customers needed per group")
note(ws, r, "Change the yellow cells. Two-sided test of two proportions (same formula as the notebooks and R's power.prop.test).")
r += 1
inputs = [("Baseline 90-day reorder rate (control)", 0.591619, PCT,
           "Observed rate for customers whose last purchase was 30–120 days before 1 Sep 2011 (1,408 customers)."),
          ("Lift to detect (percentage points)", 0.05, PCT, "Example: 5% = from 59.2% to 64.2%."),
          ("Significance level (α)", 0.05, '0.00', "Probability of a false positive."),
          ("Power (1 − β)", 0.80, '0%', "Probability of detecting the lift if it is real."),
          ("Eligible customers available", 1408, INT, "Customers eligible in one monthly cohort.")]
IN = {}
for k, (lab, val, fmt, com) in enumerate(inputs):
    ws.cell(row=r + k, column=1, value=lab).font = f()
    c = ws.cell(row=r + k, column=2, value=val); c.number_format = fmt; c.fill = INPUT_FILL
    c.font = Font(name=FONT, size=11, color="0000FF"); c.border = BOX
    c.comment = Comment(com, "analysis")
    IN[k] = f"$B${r + k}"
p0, d, al, pw, n_av = IN[0], IN[1], IN[2], IN[3], IN[4]
r += len(inputs) + 1
outs = [("Treatment reorder rate", f"={p0}+{d}", PCT),
        ("Customers per group", f"=ROUNDUP((NORMSINV(1-{al}/2)*SQRT(2*(({p0}+{p0}+{d})/2)*(1-({p0}+{p0}+{d})/2))"
                                f"+NORMSINV({pw})*SQRT({p0}*(1-{p0})+({p0}+{d})*(1-{p0}-{d})))^2/{d}^2,0)", INT),
        ("Customers in total", None, INT),
        ("Total ÷ eligible customers", None, '0.0"×"'),
        ("Enough customers in one cohort?", None, None)]
for k, (lab, fml, fmt) in enumerate(outs):
    ws.cell(row=r + k, column=1, value=lab).font = f(11, True)
    c = ws.cell(row=r + k, column=2, value=fml); c.font = f(11, True); c.border = BOX
    if fmt: c.number_format = fmt
ws.cell(row=r + 2, column=2, value=f"=2*B{r + 1}")
ws.cell(row=r + 3, column=2, value=f"=B{r + 2}/{n_av}")
ws.cell(row=r + 4, column=2, value=f'=IF(B{r + 2}<={n_av},"Yes","No: pool cohorts or widen eligibility")')
CALC_N = f"B{r + 1}"
r += len(outs) + 2
r = heading(ws, r, "Sample sizes for common lifts (from the notebooks)")
abt = ab[["lift_pp", "p_treatment", "n_per_group", "n_total", "share_of_eligible"]].copy()
abt["lift_pp"] = abt["lift_pp"] / 100
first, last = table(ws, abt, r, 1, {"lift_pp": '+0.0%', "p_treatment": PCT, "n_per_group": INT, "n_total": INT,
                                    "share_of_eligible": '0.0"×"'},
                    headers=["Lift (points)", "Treatment rate", "Per group", "Total", "Total ÷ eligible"])
ch = BarChart(); ch.type = "col"
ch.add_data(Reference(ws, min_col=3, min_row=r, max_row=last), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=first, max_row=last))
style_chart(ch, "Customers per group by lift to detect", w=14, h=6.5); ch.legend = None
color_series(ch, [ORANGE]); ch.y_axis.numFmt = '#,##0'
ch.dataLabels = DataLabelList(); ch.dataLabels.showVal = True
for k in ("showCatName", "showSerName", "showLegendKey", "showPercent"):
    setattr(ch.dataLabels, k, False)
ws.add_chart(ch, f"F{r - 16}")
note(ws, last + 1, "With all 1,408 eligible customers (704 per group) the smallest reliably detectable lift is about 7 points.")

# ================================================================ data sheets
def data_sheet(name, title, df, fmts, heads, widths):
    ws = sheet(name, title, "Filter with the arrows in the header row.", widths)
    tname = name.replace(" ", "_")
    first, last = table(ws, df, 5, 1, fmts, name=tname, headers=heads)
    ws.freeze_panes = "A6"
    return ws

rfm2 = rfm.assign(cluster_name=rfm["cluster"].map(CLUSTER_NAMES))
data_sheet("Data_Customers", "Year 2 customers: RFM scores, segment and cluster", rfm2,
           {"monetary": GBP2, "recency_days": INT, "frequency": INT},
           ["Customer ID", "Days since last purchase", "Purchase days", "Net revenue", "R", "F", "M", "RFM segment",
            "Cluster", "Cluster name"],
           {"A": 13, "B": 14, "C": 11, "D": 13, "E": 6, "F": 6, "G": 6, "H": 18, "I": 9, "J": 20})
data_sheet("Data_Rules", "All association rules (support ≥ 1%, confidence ≥ 30%)",
           rules[["lhs", "rhs", "n_lhs", "support", "confidence", "lift", "count"]],
           {"support": PCT, "confidence": '0%', "lift": '0.0', "count": INT},
           ["If the basket has…", "…it also has", "Products on left", "Support", "Confidence", "Lift", "Baskets"],
           {"A": 62, "B": 40, "C": 10, "D": 10, "E": 11, "F": 8, "G": 9})
ai2 = ai.sort_values("score", ascending=False).copy(); ai2["invoice"] = ai2["invoice"].astype(str)
for k in ["has_customer", "is_uk"]:
    ai2[k] = ai2[k].map({True: "Yes", False: "No"})
data_sheet("Data_Anomalies", "All flagged invoices (Isolation Forest top 1%)", ai2,
           {"date": DATE, "value": GBP2, "nonproduct_share": '0%', "max_price_dev": DEC2, "cancelled_share": '0%',
            "score": DEC3, "qty": INT},
           ["Invoice", "Date", "Lines", "Quantity", "Value", "Non-product share", "Max price deviation (log)",
            "Cancelled share", "Customer ID", "UK", "Hour", "Score"],
           {"A": 10, "B": 12, "C": 7, "D": 9, "E": 11, "F": 11, "G": 12, "H": 11, "I": 10, "J": 6, "K": 6, "L": 8})

# ================================================================ dictionary
ws = sheet("Dictionary", "Data dictionary", "Definitions used across the workbook", {"A": 24, "B": 26, "C": 90})
defs = [
    ("General", "Net revenue", "Gross product sales minus product cancellations, GBP. Excludes postage, fees and manual adjustments."),
    ("General", "Year 1 / Year 2", "1 Dec 2009 – 30 Nov 2010 / 1 Dec 2010 – 30 Nov 2011."),
    ("General", "p-value", "Probability of a result at least this extreme if there were no real difference. Shown as < 0.001 when tiny."),
    ("BQ1", "Value per order", "Net revenue ÷ orders (invoices with kept product lines)."),
    ("BQ1", "Cancel rate", "Cancelled value ÷ gross sales."),
    ("BQ3", "Effect per SD", "Approximate % change in (1 + Year 2 revenue) for a one-standard-deviation increase in the Year 1 measure."),
    ("BQ3/BQ6", "Odds ratio", "Multiplicative change in the odds of the outcome per unit (or per SD) of the factor; 1 = no effect."),
    ("BQ3/BQ6", "AUC / Gini / KS", "Ranking quality on the test year: AUC 0.5 = random, 1 = perfect; Gini = 2·AUC − 1; KS = max gap between cumulative distributions."),
    ("BQ4", "Recency / Frequency / Monetary", "Days since last purchase (to 1 Dec 2011) / distinct purchase days / net revenue, Year 2."),
    ("BQ4", "R, F, M scores", "Quintile scores 1–5 (5 = best); ties broken by customer ID."),
    ("BQ4", "ABC class", "A = products making the first 80% of net revenue, B = next 15%, C = last 5%."),
    ("BQ5", "Support / Confidence / Lift", "Share of baskets with all products / P(B | A) / confidence ÷ support of B."),
    ("BQ6", "MAE / RMSE / MAPE / WAPE / Bias", "Mean absolute error / root mean squared error / mean absolute % error / total absolute error ÷ total actual / total error ÷ total actual."),
    ("BQ6", "Gains table", "Customers ranked by predicted probability of buying again, split into ten equal groups."),
    ("BQ7", "Deviation (log)", "log(actual ÷ expected); 0.5 ≈ 65% above expected."),
    ("BQ7", "Isolation Forest score", "Higher = easier to isolate by random splits = more unusual."),
    ("BQ8", "Lift (A/B test)", "Increase in the 90-day reorder rate, in percentage points (not the BQ5 lift)."),
    ("BQ8", "Bonferroni", "Significance threshold divided by the number of tests, to limit false positives across several tests."),
]
d = pd.DataFrame(defs, columns=["Sheet", "Term", "Definition"])
table(ws, d, 5, 1, {}, headers=["Sheet", "Term", "Definition"])
for row_ in ws.iter_rows(min_row=6, max_row=5 + len(d)):
    row_[2].alignment = Alignment(wrap_text=True, vertical="top")

# ================================================================ Summary (built last, placed second)
ws = sheet("Summary", "Summary: eight business questions answered",
           "Headline numbers are live links to the BQ sheets.", {"A": 8, "B": 42, "C": 90})
wb.move_sheet("Summary", offset=-(len(wb.sheetnames) - 2))
r = heading(ws, 5, "Headline numbers", col=2)
kpis = [("Net revenue, Year 2", f"='BQ1 Trend'!L{YR_NET_ROW}", GBP),
        ("Change vs Year 1", f"='BQ1 Trend'!M{YR_NET_ROW}", '+0.0%;-0.0%'),
        ("Orders, change vs Year 1", f"='BQ1 Trend'!M{YR_ORD_ROW}", '+0.0%;-0.0%'),
        ("Value per order, change vs Year 1", f"='BQ1 Trend'!M{YR_AOV_ROW}", '+0.0%;-0.0%'),
        ("Champions: share of revenue", f"='BQ4 Segments'!E{SEG_FIRST}", '0%'),
        ("Next-quarter forecast (13 weeks)", f"='BQ6 Forecast'!{FQ_TOTAL}", GBPK),
        ("A/B test: customers per group for +5 pts", f"='BQ8 Tests'!{CALC_N}", INT)]
for k, (lab, fml, fmt) in enumerate(kpis):
    ws.cell(row=r + k, column=2, value=lab).font = f()
    c = ws.cell(row=r + k, column=3, value=fml); c.number_format = fmt; c.font = f(12, True)
    c.alignment = Alignment(horizontal="left")
ws.cell(row=r + len(kpis) - 1, column=3).comment = Comment("Live: changes with the calculator inputs on the BQ8 sheet.", "analysis")
r += len(kpis) + 1
r = heading(ws, r, "Answers", col=2)
answers = [
    ("BQ1", "How is the business trending?", "Flat. Net revenue +1.9% year on year, not significant once seasonality is controlled. Fewer orders (−3.9%) but larger ones (about +6% per order)."),
    ("BQ2", "What repeats?", "One strong yearly peak: Sep–Nov brings 36–38% of annual revenue, November about 15%. A business week (closed Saturdays) and office hours."),
    ("BQ3", "What drives value and cancellations?", "Order frequency is the strongest predictor of next-year value. Cancellations are driven by mispricing (odds ×17.8), higher prices and non-UK customers, not by large orders."),
    ("BQ4", "Which segments exist?", "17% of customers bring 65% of revenue (VIP regulars). A 'mid-value, cooling' group (29% of customers, £1.9M) is the main retention opportunity. 21% of products make 80% of revenue."),
    ("BQ5", "What is bought together?", "Variants of the same range: herb markers (lift up to 79), Regency teaware colours, jumbo bag prints."),
    ("BQ6", "What comes next?", "Next quarter ≈ £1.9M. Models beat 'same week last year' only marginally (WAPE 14.8% vs 15.7%). Repeat purchase is predictable (AUC 0.75 one year ahead)."),
    ("BQ7", "What is unusual?", "7 of 596 days, mostly calendar effects. Unusual invoices are single-line manual non-product entries, often non-UK or unidentified and later reversed."),
    ("BQ8", "Are differences real; how to test a campaign?", "Non-UK orders are 1.6× larger and Q4 cancellations 25% lower (both significant). A win-back A/B test needs about 1,500 customers per group to detect +5 points."),
]
for j, h in enumerate(["#", "Question", "Answer"]):
    c = ws.cell(row=r, column=1 + j, value=h); c.font = f(11, True); c.fill = HEAD_FILL; c.border = BOX
for k, (bq, qn, ans) in enumerate(answers, start=1):
    sheetname = [s for s in wb.sheetnames if s.startswith(bq + " ")][0]
    c = ws.cell(row=r + k, column=1, value=f'=HYPERLINK("#\'{sheetname}\'!A1","{bq}")'); c.font = f(11, True, "1565C0")
    ws.cell(row=r + k, column=2, value=qn).font = f(11, True)
    c = ws.cell(row=r + k, column=3, value=ans); c.font = f(); c.alignment = Alignment(wrap_text=True, vertical="top")
    for col_ in (1, 2, 3):
        ws.cell(row=r + k, column=col_).border = BOX
        ws.cell(row=r + k, column=col_).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r + k].height = 32
r += len(answers) + 2
r = heading(ws, r, "Recommendations", col=2)
recs = ["Protect the VIP regulars (17% of customers, 65% of revenue): stock availability for A-class products and account-level service.",
        "Win back mid-value, cooling customers and nurture newcomers towards a second and third order; prove the effect with a properly sized A/B test first.",
        "Plan the peak from September, not October, and commit Christmas lines early (75% of their volume sells in Q4). Use last year's weekly profile, adjusted for trend, as the forecast baseline.",
        "Sell ranges as sets: bundles for herb markers and Regency teaware, 'complete the set' recommendations, replenish all variants together.",
        "Add two finance controls: a price check at order entry, and a monthly review of single-line manual non-product entries; capture the customer ID on manual entries."]
for k, txt in enumerate(recs, start=1):
    ws.cell(row=r, column=2, value=f"{k}.").font = f(11, True)
    c = ws.cell(row=r, column=3, value=txt); c.font = f(); c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = 30
    ws.cell(row=r, column=2).alignment = Alignment(horizontal="right", vertical="top")
    r += 1
r += 1
r = heading(ws, r, "Limitations", col=2)
c = ws.cell(row=r, column=3, value="Two years of history limit forecasting; no costs or margins (revenue, not profit); no marketing, web or category data; "
                                   "group differences are associations; only an experiment (BQ8) can establish cause and effect.")
c.font = f(); c.alignment = Alignment(wrap_text=True, vertical="top"); ws.row_dimensions[r].height = 30

# print setup
for s in wb.worksheets:
    s.page_setup.orientation = "landscape"; s.page_setup.fitToWidth = 1; s.page_setup.fitToHeight = 0
    s.sheet_properties.pageSetUpPr.fitToPage = True
wb.active = 0
OUT.parent.mkdir(parents=True, exist_ok=True)
wb.save(OUT)
print("saved", OUT, wb.sheetnames)
