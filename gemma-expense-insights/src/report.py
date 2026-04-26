"""Compose KPIs into a prompt for Gemma; receive a written narrative back."""
from __future__ import annotations

import pandas as pd

from .llm_client import OllamaClient


def build_report_prompt(
    kpis: dict,
    monthly: pd.DataFrame,
    top_merchants: pd.DataFrame,
    subscriptions: pd.DataFrame,
    mom_delta: pd.DataFrame,
) -> str:
    monthly_md = monthly.to_markdown()
    top_md = top_merchants.to_markdown(index=False)
    subs_md = (
        subscriptions[["description", "abs_amount", "months", "total"]].to_markdown(index=False)
        if not subscriptions.empty
        else "(none detected)"
    )
    mom_md = mom_delta.to_markdown(index=False) if not mom_delta.empty else "(only one month of data)"

    return f"""You are a personal-finance analyst writing for an Australian household.
All figures are AUD. Be concise, direct, and quantitative. No fluff.

## Source data (already aggregated; do NOT re-do arithmetic — quote the numbers as given)

### Headline KPIs
- Date range: {kpis['date_range'][0]} to {kpis['date_range'][1]} ({kpis['months_covered']} months)
- Total spend: ${kpis['total_spend']:,.2f}
- Total income: ${kpis['total_income']:,.2f}
- Net: ${kpis['net']:,.2f}

### Monthly spend by category
{monthly_md}

### Top merchants by spend
{top_md}

### Detected recurring/subscription charges
{subs_md}

### Month-over-month change (latest vs prior month)
{mom_md}

## Your task

Produce a Markdown report with these EXACT sections:

### 1. Headline
Two sentences. State total spend, net position, and the single most notable pattern.

### 2. Where the money went
A short paragraph naming the top 3 categories by spend and what they typically buy.

### 3. Reduction opportunities
A numbered list of 3 to 5 SPECIFIC, actionable suggestions. Each must:
- Name the category or merchant
- State the current monthly cost (quote the number from the data)
- State a realistic monthly saving target ($)
- Suggest a concrete action (cancel X, switch from Y to Z, cap dining at $N/week)

### 4. Watch-list
One paragraph on the categories with the largest month-over-month INCREASE that warrant monitoring.

Do not invent numbers. Do not hedge with "consider possibly". Be direct.
"""


def generate_report(
    *,
    kpis: dict,
    monthly: pd.DataFrame,
    top_merchants_df: pd.DataFrame,
    subscriptions: pd.DataFrame,
    mom_delta: pd.DataFrame,
    client: OllamaClient,
) -> str:
    prompt = build_report_prompt(kpis, monthly, top_merchants_df, subscriptions, mom_delta)
    # Reports need more tokens than classification.
    saved_max = client.max_tokens
    client.max_tokens = 1200
    try:
        return client.generate(prompt, json_mode=False)
    finally:
        client.max_tokens = saved_max
