"""Pandas-based aggregations. All arithmetic happens here, NOT in the LLM."""
from __future__ import annotations

import pandas as pd

EXCLUDE_FROM_SPEND = {"Income", "Transfers"}


def monthly_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Wide table: rows = month, cols = category, values = total spend (positive)."""
    spend = df[df["amount"] < 0].copy()
    spend["month"] = spend["date"].dt.to_period("M").astype(str)
    spend["spend"] = spend["amount"].abs()
    pivot = (
        spend.pivot_table(
            index="month", columns="category", values="spend", aggfunc="sum", fill_value=0
        )
        .round(2)
        .sort_index()
    )
    pivot["TOTAL"] = pivot.sum(axis=1)
    return pivot


def top_merchants(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    spend = df[df["amount"] < 0].copy()
    spend["spend"] = spend["amount"].abs()
    return (
        spend.groupby("description", as_index=False)
        .agg(total=("spend", "sum"), count=("spend", "size"))
        .sort_values("total", ascending=False)
        .head(n)
        .round(2)
    )


def detect_subscriptions(df: pd.DataFrame, min_months: int = 2) -> pd.DataFrame:
    """Recurring near-identical-amount charges across multiple months.

    A charge counts as a subscription if the same merchant appears in >= min_months
    distinct months with amounts within $1 of each other.
    """
    spend = df[df["amount"] < 0].copy()
    spend["month"] = spend["date"].dt.to_period("M").astype(str)
    spend["abs_amount"] = spend["amount"].abs().round(0)

    grouped = (
        spend.groupby(["description", "abs_amount"])
        .agg(months=("month", "nunique"), total=("amount", lambda s: s.abs().sum()))
        .reset_index()
    )
    subs = grouped[grouped["months"] >= min_months].sort_values("total", ascending=False)
    return subs.round(2)


def month_over_month_delta(monthly: pd.DataFrame) -> pd.DataFrame:
    """For each category, how much higher/lower this month vs the previous month."""
    if len(monthly) < 2:
        return pd.DataFrame()
    last_two = monthly.iloc[-2:].drop(columns=["TOTAL"], errors="ignore")
    delta = (last_two.iloc[1] - last_two.iloc[0]).sort_values(ascending=False)
    return pd.DataFrame(
        {
            "category": delta.index,
            "previous": last_two.iloc[0].values,
            "current": last_two.iloc[1].values,
            "delta": delta.values,
        }
    ).round(2)


def kpi_summary(df: pd.DataFrame) -> dict:
    spend_df = df[df["amount"] < 0]
    income_df = df[df["category"] == "Income"]
    return {
        "transactions": int(len(df)),
        "spend_transactions": int(len(spend_df)),
        "total_spend": round(float(spend_df["amount"].abs().sum()), 2),
        "total_income": round(float(income_df["amount"].sum()), 2),
        "net": round(float(df["amount"].sum()), 2),
        "date_range": [
            df["date"].min().strftime("%Y-%m-%d"),
            df["date"].max().strftime("%Y-%m-%d"),
        ],
        "months_covered": int(df["date"].dt.to_period("M").nunique()),
    }
