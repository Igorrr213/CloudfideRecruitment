from pathlib import Path

import pandas as pd

from solution import add_virtual_column

BASE_DIR = Path(__file__).resolve().parent
SALES_PATH = BASE_DIR / "sales.csv"
REVENUE_PATH = BASE_DIR / "revenue_by_region.csv"

COLUMNS = [
    "order_id",
    "region",
    "product",
    "quantity",
    "unit_price",
    "discount",
    "order_date",
]


def load_sales(path=SALES_PATH):
    return pd.read_csv(path, dtype=str)


def clean_sales(raw):
    df = raw.copy()
    df.columns = [column.strip() for column in df.columns]
    df = df[df["Order ID"].str.strip() != "Order ID"]
    df = df[~df["Order ID"].str.strip().str.startswith("TOTAL")]

    for column in df.columns:
        df[column] = df[column].str.strip()

    df["Region"] = df["Region"].str.title()
    df["Quantity"] = pd.to_numeric(
        df["Quantity"].str.replace(r"\s+", "", regex=True), errors="coerce"
    ).astype("Int64")

    prices = pd.to_numeric(
        df["Unit Price"].str.replace(",", ".", regex=False), errors="coerce"
    )
    df["Unit Price"] = prices.fillna(prices.groupby(df["Product"]).transform("median"))
    df["Unit Price"] = df["Unit Price"].fillna(df["Unit Price"].median())

    df["Discount"] = pd.to_numeric(
        df["Discount"].fillna("0").str.replace(",", ".", regex=False),
        errors="coerce",
    ).fillna(0.0)

    df = df.drop_duplicates().reset_index(drop=True)
    df.columns = COLUMNS
    return df


def add_revenue(df):
    return add_virtual_column(df, "quantity * unit_price - discount", "revenue")


def summarize_revenue(df):
    return (
        df.groupby("region", as_index=False)["revenue"]
        .sum()
        .astype({"revenue": "float64"})
        .sort_values("region")
        .reset_index(drop=True)
    )


def run_pipeline(input_path=SALES_PATH, output_path=REVENUE_PATH):
    sales = clean_sales(load_sales(input_path))
    summary = summarize_revenue(add_revenue(sales))
    summary.to_csv(output_path, index=False, float_format="%.2f")
    return summary


if __name__ == "__main__":
    run_pipeline()
