"""End-to-end orchestrator.

Usage:
    python run_pipeline.py --input data/sample/sample_transactions.csv --output data/processed
    python run_pipeline.py --input data/raw --output data/processed
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from src.analyse import (
    detect_subscriptions,
    kpi_summary,
    month_over_month_delta,
    monthly_by_category,
    top_merchants,
)
from src.categorise import categorise
from src.ingest import load_path
from src.llm_client import OllamaClient
from src.report import generate_report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Local Gemma expense-insights pipeline")
    p.add_argument("--input", required=True, help="CSV/PDF file or directory of them")
    p.add_argument("--output", default="data/processed", help="Output directory")
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--no-report", action="store_true", help="Skip the LLM narrative")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = OllamaClient(
        model=cfg["model"],
        base_url=cfg["ollama_url"],
        temperature=cfg["temperature"],
        max_tokens=cfg["max_tokens"],
    )

    print(f"[1/4] Ingesting from {args.input}")
    df = load_path(Path(args.input))
    print(f"      {len(df)} rows loaded, "
          f"{df['date'].min().date()} to {df['date'].max().date()}")

    print("[2/4] Categorising (rules first, Gemma fallback)")
    df = categorise(df, rules=cfg["rules"], categories=cfg["categories"], client=client)
    df.to_csv(out_dir / "categorised.csv", index=False)

    rule_pct = (df["category_source"] == "rule").mean() * 100
    llm_pct = (df["category_source"] == "llm").mean() * 100
    print(f"      Rule hits: {rule_pct:.1f}%   LLM fallback: {llm_pct:.1f}%")

    print("[3/4] Aggregating KPIs")
    monthly = monthly_by_category(df)
    monthly.to_csv(out_dir / "monthly_summary.csv")
    top = top_merchants(df)
    top.to_csv(out_dir / "top_merchants.csv", index=False)
    subs = detect_subscriptions(df)
    subs.to_csv(out_dir / "subscriptions.csv", index=False)
    mom = month_over_month_delta(monthly)
    if not mom.empty:
        mom.to_csv(out_dir / "month_over_month.csv", index=False)
    kpis = kpi_summary(df)
    (out_dir / "kpis.json").write_text(json.dumps(kpis, indent=2), encoding="utf-8")

    if args.no_report:
        print("[4/4] Skipping narrative report (--no-report)")
        return

    print("[4/4] Asking Gemma to write the narrative report (this can take 1-3 min)")
    report_md = generate_report(
        kpis=kpis,
        monthly=monthly,
        top_merchants_df=top,
        subscriptions=subs,
        mom_delta=mom,
        client=client,
    )
    (out_dir / "report.md").write_text(report_md, encoding="utf-8")

    print(f"\nDone. Outputs in {out_dir.resolve()}")
    for name in ("categorised.csv", "monthly_summary.csv", "top_merchants.csv",
                 "subscriptions.csv", "kpis.json", "report.md"):
        path = out_dir / name
        if path.exists():
            print(f"  - {path}")


if __name__ == "__main__":
    main()
