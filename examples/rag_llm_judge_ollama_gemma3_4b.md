# Cost of Running — Example: RAG + LLM-as-Judge (Local Ollama · Gemma3:4b)

> **This is a reference example** showing what a `## `cost_of_running.md` report looks like for a RAG pipeline running **entirely on local hardware** using Ollama with `Gemma3:4b`. Copy, adapt, and replace the placeholder numbers with your own measurements.

**Architecture assumed:**
- User query → local embedding model (`mxbai-embed-large` via Ollama) → local FAISS vector store → `Gemma3:4b` answer generation → `Gemma3:4b` judge evaluation
- **No external API calls.** All inference is local via Ollama.
- Hardware: Apple M2 Pro MacBook Pro, 16 GB unified memory, macOS 14

**Key difference from the GPT-4o example:** zero API cost; higher local energy and longer wall time; carbon footprint is fully measurable from local power draw.

---

<!-- COST_OF_RUNNING:START -->

## Cost of Running

**Canonical unit of work:** one end-to-end evaluated RAG query — local embedding, retrieval, answer generation (Gemma3:4b), and LLM judge evaluation (Gemma3:4b).

This is the unit a developer or evaluator invokes when testing the pipeline against one question. It is the most meaningful unit because it exercises every cost driver and all inference is local.

### Scenario table

| Scenario | Time (Runtime) | Energy | API cost | Local compute | **Total** | Carbon |
|---|---|---|---|---|---|---|
| small (3 chunks, ~700-token context) | 24 s | 0.000187 kWh | $0.00 | **$0.000022** | **$0.000022** | **0.075 gCO₂e** |
| **typical** (5 chunks, ~1 400-token context) | 41 s | 0.000319 kWh | $0.00 | **$0.000038** | **$0.000038** | **0.128 gCO₂e** |
| heavy (10 chunks, ~3 500-token context) | 82 s | 0.000683 kWh | $0.00 | **$0.000082** | **$0.000082** | **0.273 gCO₂e** |

API cost is $0.00 — the pipeline is fully local. The dominant cost driver is **electricity** for local inference.

**Cost comparison with GPT-4o (same pipeline):**  
Typical query: $0.000038 (local) vs $0.0103 (GPT-4o) — local is **~270× cheaper per query**, but wall time is **~12× longer** (41 s vs 3.5 s). Carbon for local is fully measurable; GPT-4o cloud carbon is excluded as OpenAI does not publish it per-request.

---

### Inference breakdown — typical scenario

| Step | Model | Tokens in | Tokens out | Prefill time | Gen time | Wall time |
|---|---|---|---|---|---|---|
| embedding | `mxbai-embed-large` (local) | 30 | 128-dim vector | 0.1 s | — | 0.1 s |
| FAISS retrieval | local | — | — | — | — | 0.05 s |
| generation | `Gemma3:4b` (Ollama) | 1 400 | 350 | 7.8 s | 17.5 s | 25.3 s |
| judge | `Gemma3:4b` (Ollama) | 750 | 200 | 4.2 s | 10.0 s | 14.2 s |
| **total** | | **2 180** | **550** | **12.0 s** | **27.5 s** | **~41 s** |

**Throughput assumptions (estimated, Apple M2 Pro):**
- Prefill (prompt processing): ~180 tokens/sec
- Generation (token-by-token): ~20 tokens/sec

**Status:** estimated — not yet benchmarked. Run `pytest tests/test_benchmark_rag_pipeline.py --benchmark-only` to measure actual throughput.

---

### Inference breakdown — heavy scenario

| Step | Model | Tokens in | Tokens out | Wall time |
|---|---|---|---|---|
| embedding | `mxbai-embed-large` | 30 | 128-dim vector | 0.1 s |
| FAISS retrieval | local | — | — | 0.05 s |
| generation | `Gemma3:4b` | 3 550 | 600 | 49.8 s |
| judge | `Gemma3:4b` | 1 100 | 400 | 26.1 s |
| **total** | | **4 680** | **1 000** | **~76 s** |

*(Actual measured was 82 s — the 6 s difference is attributed to model loading variance and system scheduling.)*

---

### Assumptions

| Assumption | Value | Status | Source |
|---|---|---|---|
| Gemma3:4b prefill speed | 180 tokens/sec | estimated | Ollama community benchmarks, Apple M2 Pro, April 2025 |
| Gemma3:4b generation speed | 20 tokens/sec | estimated | Ollama community benchmarks, Apple M2 Pro, April 2025 |
| Hardware power draw | 28 W (inference) / 12 W (idle) | estimated | Apple M2 Pro TDP profile; TODO: validate with sudo powermetrics |
| Electricity price | $0.12 / kWh | estimated | EU average residential, 2024 |
| Carbon intensity | 400 gCO₂e / kWh | estimated | global average, Our World in Data 2023 |
| Exchange rate | 1 USD = 0.92 EUR | estimated | approximate, April 2025 |
| Generation tokens | 1 400 in / 350 out | estimated | code inspection |
| Judge tokens | 750 in / 200 out | estimated | code inspection |

---

### Inclusions

- Local compute electricity cost for all inference steps (embedding, generation, judge)
- Carbon footprint from local electricity consumption

### Exclusions

- Vector DB infrastructure cost (local in-memory FAISS; no recurring cost)
- Document ingestion and indexing cost (one-time)
- Model download bandwidth (one-time; `Gemma3:4b` ~2.5 GB via Ollama)
- Development, testing, and evaluation infrastructure cost
- Cooling overhead (not separately measurable without datacenter-grade tools)

---

### Methodology

Energy formula: `energy_kwh = (runtime_s / 3600) × average_power_kw`  
Local compute cost: `local_compute_usd = energy_kwh × electricity_usd_per_kwh`  
Carbon: `carbon_gco2e = energy_kwh × carbon_intensity_gco2e_per_kwh`  
API cost: $0.00 (no external API calls)  
Total: `total_usd = local_compute_usd`

All formulas and assumptions are in `cost_of_running.yaml`. The Markdown report is generated from it via a small helper script in the target repository.

**Date updated:** 2025-04-13

---

### Validation and tests

```bash
# Run all cost model tests
pytest tests/test_cost_of_running.py -v

# Benchmark end-to-end pipeline (requires Ollama running locally with Gemma3:4b pulled)
pytest tests/test_benchmark_rag_pipeline.py --benchmark-only

# Measure actual power draw during inference (macOS only)
sudo powermetrics --samplers cpu_power -n 10 -i 1000 > power_log.txt

# CPU profiling (local compute is the dominant driver here)
python scripts/profile_rag_pipeline.py

# Regenerate the Markdown report from YAML
python scripts/update_cost_of_running.py
```

**TODOs:**
- `TODO: run nexteco measure -- <ollama_inference_cmd> during a typical query and record actual power draw to replace the 28W estimate`
- `TODO: benchmark actual prefill and generation throughput on target hardware (Gemma3:4b via Ollama)`
- `TODO: validate token counts by logging Ollama API usage for 10 representative queries`
- `TODO: profile with scripts/profile_rag_pipeline.py and identify if embedding or LLM inference is the CPU hotspot`
- `TODO: test on Linux hardware (nexteco measure will invoke turbostat automatically) and update carbon figures`

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
  name: "one end-to-end evaluated RAG query (fully local)"
  description: >
    A single user question processed through the full local pipeline:
    Ollama embedding, FAISS retrieval, Gemma3:4b answer generation,
    and Gemma3:4b judge evaluation.
  rationale: >
    This is what a developer or evaluator triggers when testing the
    pipeline. Running fully locally, it exercises every cost driver
    with no external API spend.

methodology:
  approach: "Green Algorithms-inspired"
  measured_vs_estimated: >
    All values are estimated from Ollama community benchmarks and code
    inspection. Throughput and power draw are not yet validated on target
    hardware. Token counts are not yet validated against Ollama usage logs.
  formula_notes:
    - "energy_kwh = (runtime_s / 3600) * average_power_kw"
    - "local_compute_usd = energy_kwh * electricity_usd_per_kwh"
    - "carbon_gco2e = energy_kwh * carbon_intensity_gco2e_per_kwh"
    - "total_api_usd = 0.0  # no external API calls"
    - "total_usd = local_compute_usd + total_api_usd"
    - "generation_time_s = tokens_in / prefill_tps + tokens_out / gen_tps"
  benchmark:
    tool: "pytest-benchmark"
    command: "pytest tests/test_benchmark_rag_pipeline.py --benchmark-only"
    status: "TODO"
    last_run: "not_run"
    hardware: "TODO"
  profiling:
    type: "cpu"
    tool: "cProfile + pstats"
    script: "scripts/profile_rag_pipeline.py"
    status: "TODO"
    rationale: >
      This is a CPU/GPU-bound local workflow (no external API calls).
      CPU profiling is warranted to identify whether the bottleneck is
      embedding, tokenization, or LLM inference, and to confirm that
      power draw assumptions are realistic.
    notes:
      - "Also run: nexteco measure -- <target_inference_script> to dynamically log metrics"
      - "On Linux: nexteco measure handles the turbostat switch automatically."
  notes:
    - "No API-call tracing needed — all inference is local via Ollama."

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
    description: "Apple M2 Pro MacBook Pro, 16 GB unified memory"
    average_power_w: 28
    source: "estimated"
    notes:
      - "Estimated from Apple M2 Pro TDP profile during sustained LLM inference."
      - "TODO: validate with: sudo powermetrics --samplers cpu_power -n 10 -i 1000"
  runtime:
    source: "estimated"
    notes:
      - "Prefill: ~180 tokens/sec on Apple M2 Pro with Ollama Gemma3:4b (community benchmarks)."
      - "Generation: ~20 tokens/sec on Apple M2 Pro with Ollama Gemma3:4b (community benchmarks)."
      - "TODO: validate with pytest-benchmark on target hardware with Ollama running."

scenarios:
  - name: "small"
    description: "Short query, 3 retrieved chunks (~700-token context), no re-ranking."
    drivers:
      - "Two local Gemma3:4b inference calls (generation + judge), short context"
    per_unit:
      runtime_s: 24
      energy_kwh: 0.000187
      local_compute_usd: 0.0000224
      api_calls: []
      total_api_usd: 0.0
      total_usd: 0.0000224
      total_eur: 0.0000206
      carbon_gco2e: 0.075
    status:
      runtime: "estimated"
      power: "estimated"
      api_pricing: "not_applicable"
    data_quality: "low"
    notes:
      - "generation: 800 in / 200 out → prefill 4.4 s + gen 10.0 s = 14.4 s"
      - "judge: 520 in / 130 out → prefill 2.9 s + gen 6.5 s = 9.4 s"
      - "total = 0.15s (embedding+retrieval) + 14.4 + 9.4 = ~24 s"

  - name: "typical"
    description: "Medium query, 5 retrieved chunks (~1 400-token context), no re-ranking."
    drivers:
      - "Two local Gemma3:4b inference calls (generation + judge), medium context"
    per_unit:
      runtime_s: 41
      energy_kwh: 0.000319
      local_compute_usd: 0.0000383
      api_calls: []
      total_api_usd: 0.0
      total_usd: 0.0000383
      total_eur: 0.0000352
      carbon_gco2e: 0.128
    status:
      runtime: "estimated"
      power: "estimated"
      api_pricing: "not_applicable"
    data_quality: "low"
    notes:
      - "generation: 1400 in / 350 out → prefill 7.8 s + gen 17.5 s = 25.3 s"
      - "judge: 750 in / 200 out → prefill 4.2 s + gen 10.0 s = 14.2 s"
      - "total = 0.15s (embedding+retrieval) + 25.3 + 14.2 = ~40 s ≈ 41 s with overhead"

  - name: "heavy"
    description: "Long query, 10 retrieved chunks (~3 500-token context), long output."
    drivers:
      - "Two local Gemma3:4b inference calls (generation + judge), large context"
    per_unit:
      runtime_s: 82
      energy_kwh: 0.000683
      local_compute_usd: 0.0000820
      api_calls: []
      total_api_usd: 0.0
      total_usd: 0.0000820
      total_eur: 0.0000754
      carbon_gco2e: 0.273
    status:
      runtime: "estimated"
      power: "estimated"
      api_pricing: "not_applicable"
    data_quality: "low"
    notes:
      - "generation: 3550 in / 600 out → prefill 19.7 s + gen 30.0 s = 49.7 s"
      - "judge: 1100 in / 400 out → prefill 6.1 s + gen 20.0 s = 26.1 s"
      - "total = 0.15s + 49.7 + 26.1 = ~76 s; 82 s observed includes Ollama scheduling"
      - "Power draw rises toward 30-32W under sustained load; 28W is conservative."

inclusions:
  - "Local compute electricity for embedding, retrieval, generation, and judge"
  - "Carbon from local electricity consumption"

exclusions:
  - "Local FAISS vector store storage (static, not a per-query cost)"
  - "Model download bandwidth (one-time, ~2.5 GB for Gemma3:4b)"
  - "Document ingestion and indexing cost (one-time)"
  - "Development and evaluation infrastructure"

todos:
  - "TODO: benchmark with pytest-benchmark on target hardware with Ollama running"
  - "TODO: execute target trace via: nexteco measure -- <ollama_inference_cmd> to accurately collect telemetry"
  - "TODO: validate token counts by logging Ollama API usage for 10 representative queries"
  - "TODO: run CPU profile with scripts/profile_rag_pipeline.py to confirm inference is the bottleneck"
  - "TODO: test on Linux hardware. nexteco measure proxies to turbostat seamlessly."
```
