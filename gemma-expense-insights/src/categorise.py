"""Two-stage categorisation:
   1. Deterministic regex rules from config.yaml  (cheap, audit-friendly)
   2. Gemma fallback for anything unmatched         (only when needed)
"""
from __future__ import annotations

import re
from typing import Iterable

import pandas as pd

from .llm_client import OllamaClient, OllamaError


def apply_rules(descriptions: Iterable[str], rules: dict[str, str]) -> list[str | None]:
    compiled = [(re.compile(pat), cat) for pat, cat in rules.items()]
    out: list[str | None] = []
    for desc in descriptions:
        match = next((cat for pat, cat in compiled if pat.search(desc)), None)
        out.append(match)
    return out


def _llm_classify_one(client: OllamaClient, description: str, categories: list[str]) -> str:
    cat_list = ", ".join(categories)
    prompt = (
        "You are a personal-finance assistant categorising an Australian bank "
        "transaction. Pick the SINGLE best category from this list:\n"
        f"  {cat_list}\n\n"
        f"Transaction description: {description!r}\n\n"
        "If genuinely unclear, choose 'Other'."
    )
    try:
        result = client.generate_json(
            prompt,
            schema_hint='{"category": "<one of the listed categories>"}',
        )
        cat = str(result.get("category", "Other")).strip()
        return cat if cat in categories else "Other"
    except OllamaError:
        return "Other"


def categorise(
    df: pd.DataFrame,
    *,
    rules: dict[str, str],
    categories: list[str],
    client: OllamaClient,
) -> pd.DataFrame:
    """Return df with two new columns: 'category' and 'category_source'."""
    df = df.copy()
    rule_hits = apply_rules(df["description"], rules)
    df["category"] = rule_hits
    df["category_source"] = ["rule" if c else None for c in rule_hits]

    # Income vs expense sign correction: positive amount + Income rule == fine.
    # For everything else, only ask the LLM about *expenses* (negative amounts)
    # to save tokens. Credits/transfers we tag with rules or 'Transfers'.
    needs_llm_mask = df["category"].isna() & (df["amount"] < 0)
    needs_llm = df.loc[needs_llm_mask, "description"].tolist()

    if needs_llm:
        print(f"  -> Asking Gemma to classify {len(needs_llm)} ambiguous transactions...")
        client.ping()
        for idx, desc in zip(df.index[needs_llm_mask], needs_llm):
            df.at[idx, "category"] = _llm_classify_one(client, desc, categories)
            df.at[idx, "category_source"] = "llm"

    # Anything still unclassified (e.g. positive amounts not matching Income rule)
    df["category"] = df["category"].fillna("Transfers")
    df["category_source"] = df["category_source"].fillna("default")
    return df
