# NextEco — Core Repository Audit Prompt

Audit this repository and implement a **small, maintainable, test-backed Cost of Running subsystem** using NextEco.

Your goal is not to write a pretty memo.
Your goal is to leave behind a **working developer toolchain inside the repository**.

Work directly in the repository.
Keep the implementation **small, auditable, boring, and durable**.

Do **not** echo or summarize this prompt in your output.

---

## Mission

Add a repository-native feature that answers:

1. Does the deliverable work?
2. What does the canonical unit of work cost in money, time, energy, and carbon?
3. Can a future contributor regenerate and validate that answer without guesswork?

The final result must feel like a **tiny developer subsystem**, not a one-off report.

---

## Non-negotiable deliverables

You must produce or update all of the following:

1. `cost_of_running.yaml` as the source of truth
2. `cost_of_running.md` generated from the YAML
3. a small helper tool to validate and render the Markdown from the YAML
4. meaningful tests
5. a reproducible benchmark for the canonical unit of work
6. maintenance notes in `AGENTS.md` if that file exists
7. a README update if the repository does not already explain the subsystem

If the repository already contains equivalent tooling, reuse and improve it instead of duplicating it.

---

## Required posture

Be strict about the following:

- do not hallucinate numbers
- do not present estimates as measurements
- do not add unnecessary infrastructure
- do not add a database, dashboard, or remote service
- do not create complexity that the repository will not maintain

Prefer:
- one YAML source of truth
- one generated Markdown report
- one tiny validation/render path
- small tests with explicit formulas
- explicit `TODO` markers where humans must validate reality

---

## Canonical unit of work

Choose **one** primary unit of work.

Good examples:
- one CLI invocation
- one API request
- one inference
- one batch job
- one report generation
- one training run

If the repository contains multiple services or packages, choose the most central or most expensive unit of work and explicitly list the others as out of scope.

Do not keep the unit vague.

---

## Cost model requirements

Estimate, per canonical unit of work:

- money
- wall-clock time
- energy
- carbon

If the repository mixes local compute and external paid APIs, split:

- local compute cost
- external API cost
- total cost

If storage, GPU rental, network egress, or other recurring costs are materially relevant, include them.
Otherwise explicitly exclude them.

---

## Honesty taxonomy

Every important numeric input or result should clearly communicate one of:

- `measured`
- `estimated`
- `placeholder`
- `TODO`

Use that taxonomy consistently.

An honest placeholder is better than a fabricated number.

---

## Method

Use , auditable formulas.

For local compute when direct measurement is unavailable:

```text
energy_kwh = runtime_hours × average_power_kw
electricity_cost = energy_kwh × electricity_price_per_kwh
carbon_gco2e = energy_kwh × grid_carbon_intensity_gco2e_per_kwh
```

Whenever possible, utilize the native `nexteco measure -- <command>` toolchain rather than manually invoking raw OS tools.
Do not imply that `nexteco measure` or manual OS measurements were used unless the repository truly contains that evidence or you executed them and documented the outcome.

---

## API pricing provenance

Any API pricing recorded in the YAML must include:

- `source_url`
- `retrieved_date`

If that date is stale or uncertain, downgrade the field to `placeholder` and add a verification note.

---

## Country and deployment context

Do not guess the deployment country from the OS.

If electricity price, grid carbon intensity, or region is unknown, mark it clearly and ask for human validation through the YAML.

---

## Minimum acceptable implementation

At minimum, leave behind:

- `cost_of_running.yaml`
- `cost_of_running.md`
- a small script or package command that validates and renders the report
- one test that catches arithmetic or sync drift
- one benchmark or reproducible timing entry point (ideally executed via `nexteco measure`)

This minimum must be genuinely useful.

---

## Preferred implementation shape

If the repository language makes it natural, prefer a tiny CLI or package command such as:

- `validate`
- `render`
- `init`

The subsystem should be understandable in under 5 minutes by a human reviewer.

---

## Benchmarks

Add a lightweight reproducible benchmark for the canonical unit of work.

Good benchmark traits:

- deterministic input
- explicit command
- visible output
- no unnecessary runtime burden
- suitable for local reruns

If exact benchmarking is blocked, add the smallest credible scaffold and mark what remains for human validation.

---

## Tests

Add or extend tests that verify at least one of:

- arithmetic coherence
- required field presence
- sync between YAML and Markdown
- stale pricing metadata handling
- scenario total consistency

Tests should fail for meaningful reasons.

---

## Output style

The repository output should be:

- small
- explicit
- reproducible
- reviewable in pull requests
- maintainable by non-authors

Do not optimize for flourish.
Optimize for durability.

---

## Final reminder

Turn cost estimation into an engineering asset.

Not a speech.
Not a dashboard.
Not a hallucination.
