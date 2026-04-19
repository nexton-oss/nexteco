# NextEco — Advanced Repository Audit Prompt

Audit this repository and implement a **small, test-backed, profiling-aware Cost of Running subsystem** using NextEco.

This version is for repositories where runtime, memory, energy, hardware behavior, or external API decomposition truly matter.

Work directly in the repository.
Keep the implementation **small, auditable, and maintainable**.
Do **not** echo or summarize this prompt in your output.

---

## Mission

Leave behind a working subsystem that answers:

1. Does the deliverable work?
2. What does the canonical unit of work cost in money, time, energy, and carbon?
3. Where does that cost come from?
4. Can a future contributor re-run the validation, rendering, benchmark, and lightweight profiling path?

This must still feel like a **tiny developer tool**, not a heavyweight observability project.

---

## Use this advanced mode when

Use this mode when at least one of the following is true:

- runtime is a visible product concern
- local compute dominates cost
- the workload is GPU-heavy or memory-sensitive
- the unit of work contains multiple external API calls that deserve decomposition
- the repository already contains a benchmark or profiling culture
- the standard core flow would hide an important performance truth

If none of those apply, prefer `core.md`.

---

## Non-negotiable deliverables

You must produce or improve:

1. `cost_of_running.yaml`
2. `cost_of_running.md`
3. a small validation/render tool
4. meaningful tests
5. a reproducible benchmark
6. a lightweight profiling path when warranted
7. README or local docs if the subsystem is otherwise undiscoverable
8. `AGENTS.md` notes if that file exists

Reuse existing repository tooling whenever possible.

---

## What “profiling-aware” means

It does **not** mean adding heavy observability infrastructure.

It means adding the smallest credible path that helps a maintainer understand cost drivers, for example:

- CPU time
- wall-clock time
- peak memory
- API call counts
- token volume
- per-stage runtime
- local versus remote cost split

The profiling path can be a script, benchmark flag, optional trace, or documented command.

---

## Decision rule for profiling

Add a profiling path when at least one is true:

- the canonical unit of work is non-trivial in runtime
- memory pressure is likely relevant
- multiple API calls drive money or latency
- the workload has a meaningful pipeline with multiple stages
- performance tuning is plausibly part of maintenance

If the workload is trivial, document that profiling was intentionally kept minimal.

---

## Cost model requirements

Estimate, per canonical unit of work:

- money
- time
- energy
- carbon

If the project mixes local compute and paid APIs, separate:

- local compute cost
- external API cost
- total cost

When useful, break costs down by stage.

---

## Honesty and provenance

Keep the same honesty taxonomy throughout:

- `measured`
- `estimated`
- `placeholder`
- `TODO`

Do not blur them.

Any API price must carry:

- `source_url`
- `retrieved_date`

If freshness is uncertain, downgrade confidence and say so.

---

## Platform-aware guidance

When local compute matters, use the `nexteco measure -- <command>` subsystem. This command abstracts away OS-specific tools like:

- `sudo powermetrics` on macOS
- `sudo turbostat` or `sudo powertop` on Linux
- `typeperf` or `perfmon` on Windows

Do not claim those measurements happened unless you actually ran `nexteco measure` and documented the resulting artifact.

When direct energy measurement is unavailable, use explicit estimated formulas and explain the assumption path.

---

## Preferred advanced implementation

A good advanced result often includes:

- a CLI or script that validates and renders
- a benchmark command
- a profiling command or optional flag
- scenario decomposition in YAML
- generated Markdown that surfaces stage-level costs or caveats

Still keep it small.

---

## Tests

Add tests that cover at least some of the following:

- arithmetic coherence
- scenario consistency
- stale metadata detection
- report synchronization
- profiling output shape
- benchmark command contract

Tests must protect the subsystem from silent drift.

---

## Benchmark and profile design

Favor  commands that a maintainer can understand quickly.

Examples of acceptable outputs:

- one JSON profile summary
- one Markdown section with stage durations
- one optional artifacts directory
- one test fixture that exercises the canonical path

Avoid complex pipelines unless the repository already justifies them.

---

## Final reminder

The advanced mode should reveal more truth, not more theater.

Make the cost model deeper.
Do not make the repository heavier than necessary.
