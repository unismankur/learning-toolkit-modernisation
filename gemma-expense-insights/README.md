# Gemma Expense Insights — Local LLM Experiment

A privacy-first pipeline that runs **Google Gemma 3** locally via Ollama to categorise bank transactions, surface reduction opportunities, and generate monthly trend summaries. **No data ever leaves your laptop.**

---

## 1. Why this stack (evaluation summary)

| Concern | Decision | Reasoning |
|---|---|---|
| Data privacy | 100% local (Ollama) | Bank data never touches a third-party API. Ollama runs on `localhost:11434` only. |
| Hardware fit (16 GB RAM, CPU-only) | **Gemma 3 4B (Q4_K_M, ~3 GB)** | Best quality/speed tradeoff on CPU. Falls back to **Gemma 3 1B** if too slow. |
| Determinism for finance | Hybrid: rules first, LLM fallback | Regex/keyword rules handle 70–80% of common transactions deterministically; LLM only for ambiguous ones. Reduces inference cost and audit risk. |
| Reproducibility | Pinned model + config + temperature 0.1 | Same prompts → same outputs (mostly). |
| License | Gemma 3 is free for commercial/personal use under the Gemma Terms of Use | Confirm at https://ai.google.dev/gemma/terms |

**What Gemma is good at here:** classification with a fixed taxonomy, short summarisation, structured JSON output.
**What it's NOT good at:** doing arithmetic on hundreds of rows. Always do aggregations in pandas, then ask Gemma to *narrate* the numbers.

---

## 2. Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐    ┌────────────────┐
│ data/raw/    │ -> │ ingest.py    │ -> │ categorise.py    │ -> │ analyse.py     │
│ CSV + PDF    │    │ normalise to │    │ rules + Gemma    │    │ pandas groupby │
│ statements   │    │ DataFrame    │    │ via Ollama       │    │ + KPIs         │
└──────────────┘    └──────────────┘    └──────────────────┘    └───────┬────────┘
                                                                        │
                                                                        v
                                                            ┌────────────────────┐
                                                            │ report.py          │
                                                            │ Gemma writes       │
                                                            │ monthly summary +  │
                                                            │ reduction ideas    │
                                                            └────────────────────┘
```

---

## 3. One-time setup (Windows)

### 3.1 Install Ollama
1. Download installer: https://ollama.com/download/windows
2. Run installer (it installs as a service that auto-starts).
3. Verify in PowerShell:
   ```powershell
   ollama --version
   ```

### 3.2 Pull Gemma 3 4B
```powershell
ollama pull gemma3:4b
```
This downloads ~3.3 GB. First inference is slower (model loads into RAM); subsequent calls are fast.

Quick smoke test:
```powershell
ollama run gemma3:4b "Reply with just OK"
```

### 3.3 Python environment
From the project folder:
```powershell
cd C:\Users\unism\GitHub\learning-toolkit-modernisation\gemma-expense-insights
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 4. Run the experiment (sample data)

The repo ships with synthetic transactions in `data/sample/sample_transactions.csv` so you can validate the pipeline before plugging in real bank data.

```powershell
python run_pipeline.py --input data/sample/sample_transactions.csv --output data/processed
```

Outputs (all written to `data/processed/`):
- `categorised.csv` — every transaction with category + confidence + source (rule vs llm)
- `monthly_summary.csv` — spend by category by month
- `report.md` — Gemma-generated narrative with reduction ideas

Expected runtime on 16 GB CPU laptop: **~2–4 min** for the 60-row sample (most time is the LLM categorising ambiguous rows + writing the report).

---

## 5. Plug in your real data

1. Drop CSV exports into `data/raw/` (typical bank export columns: Date, Description, Amount, Balance).
2. Drop PDF statements into `data/raw/` as well — `ingest.py` will extract tables with `pdfplumber`.
3. Run:
   ```powershell
   python run_pipeline.py --input data/raw --output data/processed
   ```

`data/raw/` and `data/processed/` are **gitignored**. Real bank data will not be committed.

---

## 6. Tuning for your use case

| If you want | Edit |
|---|---|
| Different categories | `config.yaml` → `categories` list and `rules` dict |
| Faster inference (lower quality) | `config.yaml` → `model: gemma3:1b` |
| Better quality (slower) | `ollama pull gemma3:12b` then `model: gemma3:12b` (needs ~8 GB RAM free) |
| Different reduction heuristics | `src/report.py` → `build_report_prompt()` |

---

## 7. Validation checklist before trusting outputs

- Spot-check 20 random LLM-categorised rows in `categorised.csv`. Aim for ≥90% accuracy. If lower, expand `rules` in `config.yaml`.
- Reconcile monthly totals in `monthly_summary.csv` against your bank's own monthly summary. They should match to the cent.
- The narrative in `report.md` is *suggestion-grade*, not advice. Treat it as a prompt for your own judgement.
