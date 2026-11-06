"""
clean_data.py
Applies the decision log in docs/02_data_quality_findings.md (T1-T12) to the
raw Online Retail II data and saves two analysis-ready tables:

    data/processed/sales_clean.parquet     product, shipping and other lines
    data/processed/cancellations.parquet   cancellation lines (for net revenue)

Usage (from the project folder, with the environment active):
    python src/clean_data.py
"""
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_DIR / "data" / "raw" / "online_retail_ii.parquet"
OUT_DIR = PROJECT_DIR / "data" / "processed"

# T6: non-product stock codes (explicit list; every other code is a product)
NON_PRODUCT_CODES = {
    "shipping": {"POST", "DOT", "C2", "C3"},
    "fee": {"AMAZONFEE", "BANK CHARGES", "CRUK"},
    "adjustment": {"M", "m", "D", "S", "B", "ADJUST", "ADJUST2"},
    "test": {"TEST001", "TEST002"},
}
VOUCHER_PREFIX = "gift_"

BULK_QTY = 500                           # T9: about the 99.9th percentile of quantity (P8)
LAST_COMPLETE_MONTH_END = "2011-12-01"   # T10: December 2011 has only 8 trading days


class StepLog:
    """Records rows removed at each step, for the reconciliation printout."""

    def __init__(self, df):
        self.rows = []
        self.current = len(df)
        self.rows.append({"step": "Raw data", "removed": 0, "remaining": self.current})

    def record(self, step, df):
        removed = self.current - len(df)
        self.current = len(df)
        self.rows.append({"step": step, "removed": removed, "remaining": self.current})

    def show(self):
        print(pd.DataFrame(self.rows).to_string(index=False,
              formatters={"removed": "{:,}".format, "remaining": "{:,}".format}))


def load_raw():
    df = pd.read_parquet(RAW_PATH)
    return df.rename(columns={
        "Invoice": "invoice", "StockCode": "stock_code", "Description": "description",
        "Quantity": "quantity", "InvoiceDate": "invoice_date", "Price": "price",
        "Customer ID": "customer_id", "Country": "country",
    })


def remove_invalid_lines(df, log):
    """T1-T4: remove rows that are not sales or cancellations of sales."""
    df = df.drop_duplicates()                                          # T1
    log.record("T1 Remove exact duplicates", df)

    df = df.loc[~df["invoice"].str.startswith("A")]                    # T2
    log.record("T2 Remove 'A' bad-debt adjustments", df)

    is_cancel = df["invoice"].str.startswith("C")
    df = df.loc[~((df["quantity"] < 0) & ~is_cancel)]                  # T3
    log.record("T3 Remove stock adjustments (negative qty, not 'C')", df)

    df = df.loc[df["price"] > 0]                                       # T4
    log.record("T4 Remove zero-price lines", df)
    return df


def standardise(df):
    """T12: clean types and codes."""
    df = df.copy()
    df["stock_code"] = df["stock_code"].str.strip()
    df["invoice"] = df["invoice"].str.strip()
    df["customer_id"] = df["customer_id"].astype("Int64")
    return df


def classify_lines(df):
    """T6: label each line as product or a non-product group."""
    df = df.copy()
    df["line_type"] = "product"
    for group, codes in NON_PRODUCT_CODES.items():
        df.loc[df["stock_code"].isin(codes), "line_type"] = group
    df.loc[df["stock_code"].str.startswith(VOUCHER_PREFIX), "line_type"] = "voucher"
    return df


def add_product_names(df):
    """T8: most frequent description per stock code becomes the product name."""
    names = (df.dropna(subset=["description"])
               .groupby("stock_code")["description"]
               .agg(lambda s: s.value_counts().index[0])
               .rename("product_name"))
    return df.merge(names, on="stock_code", how="left")


def flag_cancelled_orders(sales, cancels):
    """T5: match each cancellation to the latest earlier order with the same
    customer, product and quantity (one-to-one), and flag that order."""
    keys = ["customer_id", "stock_code", "abs_qty"]
    s = (sales.loc[sales["customer_id"].notna()]
              .assign(abs_qty=lambda x: x["quantity"])
              .reset_index()[["index", "invoice_date"] + keys]
              .sort_values("invoice_date"))
    c = (cancels.loc[cancels["customer_id"].notna()]
                .assign(abs_qty=lambda x: -x["quantity"])
                [["invoice_date"] + keys]
                .sort_values("invoice_date"))
    # merge_asof needs plain (non-nullable) key types
    for frame in (s, c):
        frame["customer_id"] = frame["customer_id"].astype("int64")

    matched = pd.merge_asof(c, s, on="invoice_date", by=keys, direction="backward")
    order_index = matched["index"].dropna().astype(int).drop_duplicates()

    sales = sales.copy()
    sales["cancelled_exact"] = sales.index.isin(order_index)
    match_rate = len(order_index) / max(len(c), 1)
    return sales, match_rate


def add_flags_and_features(df):
    """T7, T9, T10, T11: flags and date features used by later notebooks."""
    df = df.copy()
    df["has_customer"] = df["customer_id"].notna()                          # T7
    df["is_bulk"] = df["quantity"] > BULK_QTY                               # T9
    df["in_complete_month"] = df["invoice_date"] < LAST_COMPLETE_MONTH_END  # T10
    df["date"] = df["invoice_date"].dt.normalize()
    df["week_start"] = df["date"] - pd.to_timedelta(df["date"].dt.weekday, unit="D")
    df["month"] = df["invoice_date"].dt.to_period("M").dt.to_timestamp()
    df["weekday"] = df["invoice_date"].dt.day_name()                        # T11
    df["hour"] = df["invoice_date"].dt.hour
    return df


def reconcile(sales, cancels, match_rate):
    product = sales["line_type"] == "product"
    gross = sales.loc[product, "revenue"].sum()
    cancelled = -cancels.loc[cancels["line_type"] == "product", "revenue"].sum()
    shipping = sales.loc[sales["line_type"] == "shipping", "revenue"].sum()

    print("\n--- Revenue reconciliation (GBP) ---")
    print(f"Gross product sales        £{gross:>14,.0f}")
    print(f"Less product cancellations £{cancelled:>14,.0f}")
    print(f"Net product revenue        £{gross - cancelled:>14,.0f}")
    print(f"Shipping income            £{shipping:>14,.0f}  (reported separately)")

    print("\n--- Line types in sales table ---")
    print(sales["line_type"].value_counts().to_string())

    print("\n--- Flags ---")
    print(f"Lines with a customer       {sales['has_customer'].mean():6.1%}")
    print(f"Bulk lines (qty > {BULK_QTY})     {sales['is_bulk'].sum():>6,}")
    print(f"Orders cancelled exactly    {sales['cancelled_exact'].sum():>6,}"
          f"  ({match_rate:.1%} of cancellations with a customer matched)")
    print(f"Sales lines in Dec 2011     {(~sales['in_complete_month']).sum():>6,}")

def validate(sales, cancels, expected_total):
    """Output checks: every rule in the decision log must hold after cleaning.
    All checks run; the script stops with a list of failures if any fail."""
    product_cancels = cancels.loc[cancels["line_type"] == "product"]
    checks = [
        ("C01 Sales + cancellations = rows after T4",
         len(sales) + len(cancels) == expected_total),
        ("C02 No exact duplicate sales lines (T1)",
         not sales.duplicated(subset=["invoice", "stock_code", "description", "quantity",
         "price", "invoice_date", "customer_id",
         "country"]).any()),
        ("C03 No 'A' invoices remain (T2)",
         not sales["invoice"].str.startswith("A").any()
         and not cancels["invoice"].str.startswith("A").any()),
        ("C04 All sales quantities > 0 (T3)", (sales["quantity"] > 0).all()),
        ("C05 All prices > 0 (T4)",
         (sales["price"] > 0).all() and (cancels["price"] > 0).all()),
        ("C06 Sales table has no 'C' invoices (T5)",
         not sales["invoice"].str.startswith("C").any()),
        ("C07 Cancellation table has only 'C' invoices (T5)",
         cancels["invoice"].str.startswith("C").all()),
        ("C08 Product cancellations have negative quantity (T5)",
         (product_cancels["quantity"] < 0).all()),
        ("C09 Line types are from the allowed list (T6)",
         set(sales["line_type"]) | set(cancels["line_type"])
         <= {"product", "shipping", "fee", "adjustment", "voucher", "test"}),
        ("C10 Non-product codes are never labelled 'product' (T6)",
         not sales.loc[sales["line_type"] == "product", "stock_code"]
         .isin(set().union(*NON_PRODUCT_CODES.values())).any()),
        ("C11 Stock codes have no leading/trailing spaces (T12)",
         (sales["stock_code"] == sales["stock_code"].str.strip()).all()),
        ("C12 Customer ID is an integer type (T12)",
         str(sales["customer_id"].dtype) == "Int64"),
        ("C13 Revenue = quantity x price",
         ((sales["revenue"] - sales["quantity"] * sales["price"]).abs() < 1e-6).all()),
        ("C14 Partial-month flag only marks December 2011 (T10)",
         (sales.loc[~sales["in_complete_month"], "invoice_date"] >= LAST_COMPLETE_MONTH_END).all()),
        ("C15 Cancelled orders flagged only for known customers (T5)",
         sales.loc[sales["cancelled_exact"], "customer_id"].notna().all()),
    ]

    print("--- Output checks ---")
    for name, passed in checks:
        print(f"{'PASS' if passed else 'FAIL'}  {name}")

    # Soft checks: reported for monitoring, not enforced
    missing_names = sales.loc[sales["line_type"] == "product", "product_name"].isna().sum()
    print(f"INFO  Product lines without a product name: {missing_names:,}")

    failed = [name for name, passed in checks if not passed]
    if failed:
        raise AssertionError("Output checks failed: " + "; ".join(failed))
    print(f"All {len(checks)} output checks passed\n")

def main():
    raw = load_raw()
    log = StepLog(raw)

    df = remove_invalid_lines(raw, log)
    df = standardise(df)
    df = classify_lines(df)
    df["revenue"] = df["quantity"] * df["price"]

    is_cancel = df["invoice"].str.startswith("C")
    sales = df.loc[~is_cancel].copy()
    cancels = df.loc[is_cancel].copy()

    sales = add_product_names(sales)
    cancels = cancels.merge(sales[["stock_code", "product_name"]].drop_duplicates(),
                            on="stock_code", how="left")
    sales, match_rate = flag_cancelled_orders(sales, cancels)
    sales = add_flags_and_features(sales)
    cancels = add_flags_and_features(cancels)

    validate(sales, cancels, log.current)          # stop before saving if a rule fails

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sales.to_parquet(OUT_DIR / "sales_clean.parquet", index=False)
    cancels.to_parquet(OUT_DIR / "cancellations.parquet", index=False)

    print("--- Row reconciliation ---")
    log.show()
    print(f"\nSplit: {len(sales):,} sales lines + {len(cancels):,} cancellation lines"
          f" = {len(sales) + len(cancels):,}")
    reconcile(sales, cancels, match_rate)
    print(f"\nSaved to {OUT_DIR}")


if __name__ == "__main__":
    main()