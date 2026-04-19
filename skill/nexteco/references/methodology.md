# Methodology

## Purpose

NextEco models the **cost of one canonical unit of work**.
That unit might be:

- one CLI run
- one API request
- one inference
- one batch job
- one training execution
- one generated report

The model should always prefer one clear unit over vague aggregate storytelling.

## Four dimensions

Every serious NextEco model aims to expose:

- money
- time
- energy
- carbon

## Local compute formulas

When direct metrology is unavailable, the estimated baseline is:

```text
energy_kwh = runtime_hours × average_power_kw
electricity_cost_usd = energy_kwh × electricity_price_usd_per_kwh
carbon_gco2e = energy_kwh × grid_carbon_intensity_gco2e_per_kwh
```

These formulas are intentionally .
The hard part is usually not algebra.
The hard part is choosing the right unit of work, separating measured from assumed values, and keeping provenance visible.

## Local versus external APIs

If a system mixes local compute and external APIs, keep the split visible:

- local compute cost
- external API cost
- total cost

This avoids flattening very different cost drivers into one number too early.

## Provenance

Any API pricing should include:

- `source_url`
- `retrieved_date`

If freshness is uncertain, degrade confidence and say so.

## Honesty taxonomy

Use these statuses consistently:

- `measured`
- `estimated`
- `placeholder`
- `TODO`

Never present an estimate as a measurement.
Never present a placeholder as a decision-grade fact.

## Country and deployment context

Do not guess the deployment country from the operating system.
Electricity price and carbon intensity often require human validation.

## Minimum viable subsystem

A good NextEco result is usually small:

- one YAML file
- one generated Markdown report
- one validation path
- one rendering path
- one small benchmark scaffold
- a few meaningful tests

That minimum is often better than a large, fragile system.
