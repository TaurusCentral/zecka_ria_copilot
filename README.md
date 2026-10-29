# RIA Copilot - ZECKATHON PS04

A reproducible, suitability-first co-pilot for a SEBI-registered Investment Adviser. It separates risk capacity from risk tolerance, builds inflation-adjusted goal plans, applies a glide path, screens unsuitable requests, performs a transparent 10-year allocation backtest, retrieves only from evidence with page/source metadata, and requires explicit adviser approval.

## Why this architecture

The LLM is not allowed to perform financial arithmetic or suitability decisions. Deterministic modules compute risk, goals, allocations, guardrails, and backtests. The research layer is evidence-first and abstains when evidence is unavailable. Every client-facing recommendation remains a draft until adviser approval.

## Run

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pytest -q
python scripts/generate_report_metrics.py
streamlit run app.py
```

## 3-minute demo path

1. Select the retiree persona and show capacity vs tolerance plus retirement protection.
2. Build a 25-year income goal and show corpus, SIP and glide path.
3. Enter `I am 68 and want small-cap only exposure` and show the block.
4. Ask `What does SEBI require for risk profiling?` and show page-level source metadata.
5. Ask an unsupported fund fact and show abstention instead of hallucination.
6. Build a plan and click adviser approval to create a tamper-evident plan hash and audit record.

## Data and claims

`data/nifty50_tri_monthly_2015_2024.csv` is transcribed from the Nifty 50 2025 whitepaper monthly return exhibit and is bundled so the backtest is reproducible offline. The debt leg is explicitly a 7% annual planning proxy, not a claimed debt-fund historical return. Replace it with an appropriate verified debt benchmark or fund NAV series for production.

AMFI adapters are included for latest NAV/scheme master and 90-day chunked history retrieval. AMC factsheets/SIDs/portfolio disclosures should be placed into the evidence store before answering fund-specific hidden questions.

## Repository map

- `ria_copilot/risk.py`: capacity and tolerance scored separately, conservative conflict resolution.
- `ria_copilot/goals.py`: corpus, SIP and glide path.
- `ria_copilot/amfi.py`: public AMFI ingestion adapter.
- `ria_copilot/portfolio.py`: NAV-derived metrics and transparent ranking.
- `ria_copilot/rag.py`: citation-carrying retrieval with abstention.
- `ria_copilot/guardrails.py`: adversarial suitability rules.
- `ria_copilot/approval.py`: mandatory human approval and plan hash.
- `scripts/generate_report_metrics.py`: single source for report numbers.
- `report/report.tex`: final report.

## Important limitations

This is adviser decision support, not autonomous advice. Planning returns and inflation are assumptions, not guarantees. The bundled backtest demonstrates the allocation engine with a benchmark/proxy pair. Fund-specific client output should be released only after current AMFI/AMC data are ingested and reviewed by the adviser.
