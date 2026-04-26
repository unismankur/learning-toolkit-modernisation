"""Ingest bank transactions from CSV and PDF sources into a single DataFrame.

Output schema (always):
    date         : datetime64[ns]
    description  : str (cleaned, single-spaced)
    amount       : float (negative = debit/spend, positive = credit/income)
    source_file  : str
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from dateutil import parser as dateparser

# Common Australian bank CSV column aliases. Extend as you encounter new banks.
COLUMN_ALIASES = {
    "date":        ["date", "transaction date", "posted date", "value date"],
    "description": ["description", "narration", "transaction details", "details", "merchant"],
    "amount":      ["amount", "amt", "transaction amount"],
    "debit":       ["debit", "withdrawals", "money out"],
    "credit":      ["credit", "deposits", "money in"],
}


def _canonical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to a canonical set: date, description, amount."""
    lower = {c.lower().strip(): c for c in df.columns}
    rename = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in lower:
                rename[lower[alias]] = canonical
                break
    df = df.rename(columns=rename)

    # If bank gave separate debit/credit columns, fold into a signed `amount`.
    if "amount" not in df.columns and {"debit", "credit"}.issubset(df.columns):
        debit = pd.to_numeric(df["debit"], errors="coerce").fillna(0)
        credit = pd.to_numeric(df["credit"], errors="coerce").fillna(0)
        df["amount"] = credit - debit

    missing = {"date", "description", "amount"} - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns after normalisation: {missing}")
    return df[["date", "description", "amount"]]


def _clean(df: pd.DataFrame, source: str) -> pd.DataFrame:
    df = df.copy()
    df["date"] = df["date"].apply(lambda x: dateparser.parse(str(x), dayfirst=True))
    df["description"] = (
        df["description"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    )
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["date", "amount"])
    df["source_file"] = source
    return df.reset_index(drop=True)


def load_csv(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    return _clean(_canonical_columns(raw), source=path.name)


def load_pdf(path: Path) -> pd.DataFrame:
    """Extract tabular transactions from a PDF statement using pdfplumber.

    Heuristic: scan every page's tables, look for rows where the first
    cell parses as a date and the last cell parses as a number. Bank
    statement layouts vary wildly — you may need to tune this per bank.
    """
    import pdfplumber  # lazy import; keeps CSV-only path light

    rows: list[dict] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                for row in table:
                    if not row or len(row) < 3:
                        continue
                    cells = [(c or "").strip() for c in row]
                    # Find first cell that looks like a date.
                    try:
                        date = dateparser.parse(cells[0], dayfirst=True, fuzzy=True)
                    except (ValueError, TypeError):
                        continue
                    # Find a numeric cell (rightmost wins — usually 'amount' col).
                    amount = None
                    for c in reversed(cells[1:]):
                        c_clean = re.sub(r"[,$\s]", "", c).replace("(", "-").replace(")", "")
                        try:
                            amount = float(c_clean)
                            break
                        except ValueError:
                            continue
                    if amount is None:
                        continue
                    description = " ".join(c for c in cells[1:-1] if c)
                    rows.append(
                        {"date": date, "description": description, "amount": amount}
                    )
    if not rows:
        return pd.DataFrame(columns=["date", "description", "amount", "source_file"])
    df = pd.DataFrame(rows)
    return _clean(df, source=path.name)


def load_path(path: Path) -> pd.DataFrame:
    """Load a single file or every CSV/PDF inside a directory."""
    path = Path(path)
    if path.is_file():
        return _dispatch(path)

    frames: list[pd.DataFrame] = []
    for child in sorted(path.iterdir()):
        if child.suffix.lower() in {".csv", ".pdf"}:
            try:
                frames.append(_dispatch(child))
            except Exception as e:
                print(f"  ! Skipping {child.name}: {e}")
    if not frames:
        raise FileNotFoundError(f"No CSV or PDF files found in {path}")
    return pd.concat(frames, ignore_index=True).sort_values("date").reset_index(drop=True)


def _dispatch(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_csv(path)
    if suffix == ".pdf":
        return load_pdf(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")
