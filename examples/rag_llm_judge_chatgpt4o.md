# Cost of Running — Example: RAG + LLM-as-Judge (OpenAI GPT-4o)

> **This is a reference example** showing what a `## `cost_of_running.md` report looks like for a typical RAG pipeline that uses ChatGPT as both the answer generator and the LLM judge. Copy, adapt, and replace the placeholder numbers with your own measurements.

**Architecture assumed:**
- User query → `text-embedding-3-small` embedding → vector store lookup (top-k chunks) → `gpt-4o` answer generation → `gpt-4o` judge evaluation
- All LLM calls are external API calls to OpenAI
- Local compute: Python application running on a developer laptop (API-bound workflow)

---

<!-- COST_OF_RUNNING:START -->

## Cost of Running

**Canonical unit of work:** one end-to-end evaluated RAG query — embedding, retrieval, answer generation, and LLM judge evaluation.

This is the unit a developer or operator invokes when testing the pipeline against one question. It is the most meaningful unit because it exercises every cost driver at once.

### Scenario table

| Scenario | Time (Runtime) | Energy (local) | API cost | Local compute | **Total** | Carbon (local) |
|---|---|---|---|---|---|---|
| small (3 chunks, ~700-token context) | 2.1 s | 0.0000072 kWh | **$0.0059** | < $0.001 | **$0.0059** | 0.003 gCO₂e |
| **typical** (5 chunks, ~1 400-token context) | 3.5 s | 0.0000117 kWh | **$0.0103** | < $0.001 | **$0.0103** | 0.005 gCO₂e |
| heavy (10 chunks + re-ranking, ~3 700-token context) | 8.2 s | 0.0000273 kWh | **$0.0310** | < $0.001 | **$0.0310** | 0.011 gCO₂e |

Local compute cost is negligible (< $0.001 per query) because this workflow is API-bound — wall time is dominated by OpenAI API latency. Energy and carbon figures cover local compute only; OpenAI data-center energy and carbon are not published per-request and are **excluded**.

---

### API call breakdown — typical scenario

| Call | Model | Tokens in | Tokens out | Cost |
|---|---|---|---|---|
| embedding | `text-embedding-3-small` | 30 | 0 | < $0.001 |
| generation | `gpt-4o` | 1 400 | 350 | $0.0065 |
| judge | `gpt-4o` | 750 | 200 | $0.0038 |
| **total_api_usd** | | **2 180** | **550** | **$0.0103** |

**Pricing source:** <https://openai.com/api/pricing> — retrieved 2025-04-13  
**Status:** estimated (token counts from code inspection; not yet validated against production API logs)

Token estimates:
- `embedding`: query string, ~30 tokens (short user question)
- `generation` in: system prompt (150 t) + user query (50 t) + 5 chunks × 240 t = 1 400 t
- `generation` out: answer, ~350 tokens (conservative)
- `judge` in: rubric (300 t) + user query (50 t) + generated answer (350 t) + framing (50 t) = 750 t
- `judge` out: structured judgment with score, ~200 tokens

---

### API call breakdown — small scenario

| Call | Model | Tokens in | Tokens out | Cost |
|---|---|---|---|---|
| embedding | `text-embedding-3-small` | 25 | 0 | < $0.001 |
| generation | `gpt-4o` | 775 | 200 | $0.0039 |
| judge | `gpt-4o` | 550 | 120 | $0.0021 |
| **total_api_usd** | | **1 350** | **320** | **$0.0059** |

---

### API call breakdown — heavy scenario (with re-ranking)

| Call | Model | Tokens in | Tokens out | Cost |
|---|---|---|---|---|
| embedding | `text-embedding-3-small` | 30 | 0 | < $0.001 |
| re-ranking | `gpt-4o` | 3 200 | 250 | $0.0108 |
| generation | `gpt-4o` | 3 550 | 600 | $0.0149 |
| judge | `gpt-4o` | 1 100 | 400 | $0.0053 |
| **total_api_usd** | | **7 880** | **1 250** | **$0.0310** |

---

### Assumptions

| Assumption | Value | Status | Source |
|---|---|---|---|
| GPT-4o input price | $2.50 / 1M tokens | estimated | openai.com/api/pricing, 2025-04-13 |
| GPT-4o output price | $10.00 / 1M tokens | estimated | openai.com/api/pricing, 2025-04-13 |
| text-embedding-3-small price | $0.020 / 1M tokens | estimated | openai.com/api/pricing, 2025-04-13 |
| Electricity price | $0.12 / kWh | estimated | EU average residential, 2024 |
| Carbon intensity | 400 gCO₂e / kWh | estimated | global average, Our World in Data 2023 |
| Local hardware power | 12 W average | estimated | laptop at low load (API-bound, mostly idle) |
| Generation token count | 1 400 in / 350 out | estimated | code inspection, not yet measured |
| Judge token count | 750 in / 200 out | estimated | code inspection, not yet measured |
| Exchange rate | 1 USD = 0.92 EUR | estimated | approximate, April 2025 |

---

### Inclusions

- OpenAI API cost: embedding, generation, and judge calls
- Local compute electricity cost during runtime

### Exclusions

- OpenAI data-center energy and carbon (not published per-request)
- Vector DB infrastructure cost (assumed local/in-memory; not recurring)
- Storage cost for the document corpus (one-time ingestion, not per-query)
- Network egress (negligible for JSON payloads)
- Development and indexing costs

---

### Methodology

Energy formula: `energy_kwh = (runtime_s / 3600) × average_power_kw`  
API cost formula: `api_call.cost_usd = (tokens_in × price_per_1m_in + tokens_out × price_per_1m_out) / 1_000_000`  
Total: `total_usd = local_compute_usd + sum(api_calls[*].cost_usd)`  
Carbon: `carbon_gco2e = energy_kwh × 400` (local compute only)

All formulas and assumptions are in `cost_of_running.yaml`. The Markdown report is generated from it via a small helper script in the target repository.

**Date updated:** 2025-04-13

---

### Validation and tests

```bash
# Run all cost model tests
pytest tests/test_cost_of_running.py -v

# Run the benchmark (measures wall-clock time for one end-to-end query)
pytest tests/test_benchmark_rag_pipeline.py --benchmark-only

# Regenerate the Markdown report from YAML
python scripts/update_cost_of_running.py

# Trace API calls and token counts for one representative query
python scripts/trace_api_calls.py
```

**TODOs:**
- `TODO: validate token counts via OpenAI API usage logs for 10 representative queries`
- `TODO: verify current GPT-4o pricing at https://openai.com/api/pricing (retrieved 2025-04-13 — re-check after 2025-07-13)`
- `TODO: measure actual runtime distribution across slow/fast network conditions`
- `TODO: confirm whether re-ranking is always triggered or only above a similarity threshold`

<!-- COST_OF_RUNNING:END -->

---

## Corresponding `cost_of_running.yaml`

```yaml
date_updated: "2025-04-13"

deployment:
  provider: "local"
  instance_type: "Apple M2 Pro MacBook Pro"
  region: "local"
  country: "global average"

workload:
  type: "inference"
  scale: "one-off evaluation query"

unit_of_work:
  name: "one end-to-end evaluated RAG query"
  description: >
    A single user question processed through the full pipeline:
    embedding, vector store retrieval, GPT-4o answer generation,
    and GPT-4o judge evaluation.
  rationale: >
    This is what an operator or evaluator triggers when assessing
    pipeline quality. It exercises every cost driver simultaneously.

methodology:
  approach: "Green Algorithms-inspired"
  measured_vs_estimated: >
    All values are estimated from code inspection. Token counts are
    not yet validated against real API usage logs. Runtime is estimated
    from typical OpenAI API latency, not benchmarked.
  formula_notes:
    - "energy_kwh = (runtime_s / 3600) * average_power_kw"
    - "local_compute_usd = energy_kwh * electricity_usd_per_kwh"
    - "carbon_gco2e = energy_kwh * carbon_intensity_gco2e_per_kwh"
    - "api_call.cost_usd = (tokens_in * price_per_1m_in + tokens_out * price_per_1m_out) / 1_000_000"
    - "total_api_usd = sum(api_calls[*].cost_usd)"
    - "total_usd = local_compute_usd + total_api_usd"
  benchmark:
    tool: "pytest-benchmark"
    command: "pytest tests/test_benchmark_rag_pipeline.py --benchmark-only"
    status: "TODO"
    last_run: "not_run"
    hardware: "TODO"
  profiling:
    type: "api_call_tracing"
    tool: "custom wrapper (scripts/trace_api_calls.py)"
    script: "scripts/trace_api_calls.py"
    status: "TODO"
    rationale: >
      Workflow is API-bound (> 90% wall time is OpenAI API latency).
      CPU profiling is not warranted. API call tracing records
      tokens_in, tokens_out, latency_ms, cost_usd per call.
  notes:
    - "OpenAI data-center energy and carbon are excluded — not published per-request."

assumptions:
  currency:
    usd_to_eur: 0.92
    source: "approximate, April 2025"
    status: "estimated"
  electricity:
    usd_per_kwh: 0.12
    region: "EU average"
    source: "Eurostat residential electricity prices 2024"
    status: "estimated"
  carbon_intensity:
    gco2e_per_kwh: 400
    region: "global average"
    source: "Our World in Data, 2023"
    status: "estimated"
  hardware:
    description: "developer laptop, CPU-idle during API calls"
    average_power_w: 12
    source: "estimated"
  runtime:
    source: "estimated"
    notes:
      - "Estimated from typical OpenAI API latency (1–2 s per call, serial calls)."
      - "TODO: validate with pytest-benchmark on target hardware."

scenarios:
  - name: "small"
    description: "Short query, 3 retrieved chunks (~700-token context), no re-ranking."
    drivers:
      - "2 GPT-4o calls (generation + judge), short context"
    per_unit:
      runtime_s: 2.1
      energy_kwh: 0.0000072
      local_compute_usd: 0.0000009
      api_calls:
        - name: "embedding"
          provider: "openai"
          model: "text-embedding-3-small"
          tokens_in: 25
          tokens_out: 0
          price_per_1m_in: 0.020
          price_per_1m_out: 0.000
          cost_usd: 0.0000005
          source_url: "https://openai.com/api/pricing"
          retrieved_date: "2025-04-13"
          status: "estimated"
        - name: "generation"
          provider: "openai"
          model: "gpt-4o"
          tokens_in: 775
          tokens_out: 200
          price_per_1m_in: 2.50
          price_per_1m_out: 10.00
          cost_usd: 0.003938
          source_url: "https://openai.com/api/pricing"
          retrieved_date: "2025-04-13"
          status: "estimated"
        - name: "judge"
          provider: "openai"
          model: "gpt-4o"
          tokens_in: 550
          tokens_out: 120
          price_per_1m_in: 2.50
          price_per_1m_out: 10.00
          cost_usd: 0.002575
          source_url: "https://openai.com/api/pricing"
          retrieved_date: "2025-04-13"
          status: "estimated"
      total_api_usd: 0.006514
      total_usd: 0.006515
      total_eur: 0.005994
      carbon_gco2e: 0.003    # local compute only
    status:
      runtime: "estimated"
      power: "estimated"
      api_pricing: "estimated"
    data_quality: "low"
    notes:
      - "Token counts from code inspection only. Must be validated via API usage logs."

  - name: "typical"
    description: "Medium query, 5 retrieved chunks (~1 400-token context), no re-ranking."
    drivers:
      - "2 GPT-4o calls (generation + judge), medium context"
    per_unit:
      runtime_s: 3.5
      energy_kwh: 0.0000117
      local_compute_usd: 0.0000014
      api_calls:
        - name: "embedding"
          provider: "openai"
          model: "text-embedding-3-small"
          tokens_in: 30
          tokens_out: 0
          price_per_1m_in: 0.020
          price_per_1m_out: 0.000
          cost_usd: 0.0000006
          source_url: "https://openai.com/api/pricing"
          retrieved_date: "2025-04-13"
          status: "estimated"
        - name: "generation"
          provider: "openai"
          model: "gpt-4o"
          tokens_in: 1400
          tokens_out: 350
          price_per_1m_in: 2.50
          price_per_1m_out: 10.00
          cost_usd: 0.006500
          source_url: "https://openai.com/api/pricing"
          retrieved_date: "2025-04-13"
          status: "estimated"
        - name: "judge"
          provider: "openai"
          model: "gpt-4o"
          tokens_in: 750
          tokens_out: 200
          price_per_1m_in: 2.50
          price_per_1m_out: 10.00
          cost_usd: 0.003875
          source_url: "https://openai.com/api/pricing"
          retrieved_date: "2025-04-13"
          status: "estimated"
      total_api_usd: 0.010376
      total_usd: 0.010377
      total_eur: 0.009547
      carbon_gco2e: 0.005    # local compute only
    status:
      runtime: "estimated"
      power: "estimated"
      api_pricing: "estimated"
    data_quality: "low"
    notes:
      - "Token counts from code inspection. Not yet validated against real API logs."

  - name: "heavy"
    description: "Long query, 10 chunks + GPT-4o re-ranking (~3 700-token context for generation)."
    drivers:
      - "3 GPT-4o calls (re-ranking + generation + judge), large context"
    per_unit:
      runtime_s: 8.2
      energy_kwh: 0.0000273
      local_compute_usd: 0.0000033
      api_calls:
        - name: "embedding"
          provider: "openai"
          model: "text-embedding-3-small"
          tokens_in: 30
          tokens_out: 0
          price_per_1m_in: 0.020
          price_per_1m_out: 0.000
          cost_usd: 0.0000006
          source_url: "https://openai.com/api/pricing"
          retrieved_date: "2025-04-13"
          status: "estimated"
        - name: "reranking"
          provider: "openai"
          model: "gpt-4o"
          tokens_in: 3200
          tokens_out: 250
          price_per_1m_in: 2.50
          price_per_1m_out: 10.00
          cost_usd: 0.010500
          source_url: "https://openai.com/api/pricing"
          retrieved_date: "2025-04-13"
          status: "estimated"
        - name: "generation"
          provider: "openai"
          model: "gpt-4o"
          tokens_in: 3550
          tokens_out: 600
          price_per_1m_in: 2.50
          price_per_1m_out: 10.00
          cost_usd: 0.014875
          source_url: "https://openai.com/api/pricing"
          retrieved_date: "2025-04-13"
          status: "estimated"
        - name: "judge"
          provider: "openai"
          model: "gpt-4o"
          tokens_in: 1100
          tokens_out: 400
          price_per_1m_in: 2.50
          price_per_1m_out: 10.00
          cost_usd: 0.006750
          source_url: "https://openai.com/api/pricing"
          retrieved_date: "2025-04-13"
          status: "estimated"
      total_api_usd: 0.032126
      total_usd: 0.032129
      total_eur: 0.029559
      carbon_gco2e: 0.011    # local compute only
    status:
      runtime: "estimated"
      power: "estimated"
      api_pricing: "estimated"
    data_quality: "low"
    notes:
      - "Re-ranking adds a large GPT-4o call. Consider a local reranker (e.g. cross-encoder) to reduce cost."

inclusions:
  - "OpenAI API cost: embedding, generation, judge, and optional re-ranking calls"
  - "Local compute electricity cost during query processing"

exclusions:
  - "OpenAI data-center energy and carbon (not published per-request)"
  - "Vector DB infrastructure cost (assumed local/in-memory)"
  - "Document ingestion and indexing cost (one-time)"
  - "Network egress (negligible for JSON API payloads)"
  - "Development, testing, and evaluation infrastructure cost"

todos:
  - "TODO: validate token counts via OpenAI API usage logs for 10 representative queries"
  - "TODO: re-verify GPT-4o pricing at https://openai.com/api/pricing — retrieved 2025-04-13, re-check after 2025-07-13"
  - "TODO: run benchmark (pytest tests/test_benchmark_rag_pipeline.py --benchmark-only) and record hardware"
  - "TODO: run API call tracer (python scripts/trace_api_calls.py) and update runtime estimates"
  - "TODO: confirm whether re-ranking is always triggered or conditional on similarity score"
  - "TODO: consider whether cloud deployment introduces additional carbon accounting"
```
