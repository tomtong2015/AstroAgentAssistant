---
name: astro-data-access-umbrella
description: Use when an astronomy task needs data access and the agent must choose between TAP/ADQL/pyvo catalogs, Gaia@AIP REST/Daiquiri, S3/Parquet object storage, local StarHorse-style datasets, plotting/cache workflows, or REANA execution.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [astronomy, data-access, catalogs, tap, s3, parquet, reana]
    related_skills: [tap-pyvo-adql-access, gaia-aip-data-access, rave-dr6-data-access, s3-parquet-astro-access, astro-catalog-plotting-cache, reana-operator, starhorse-access]
---

# Astro Data Access Umbrella

## Overview

This is the canonical entry point for astronomy data access. Use it before reaching for narrow Gaia, RAVE, S3, StarHorse, or plotting examples. The goal is to choose the right access pattern, run a minimal probe first, cache results reproducibly, and route executable scientific tasks through REANA when appropriate.

Separate three concerns:

1. **Access** — TAP/ADQL/pyvo, Gaia@AIP Daiquiri REST, S3/Parquet, HDF5-on-S3, or local files.
2. **Execution** — local smoke/probe versus full REANA task.
3. **Presentation** — publication-ready plots, provenance, and cached outputs.

## When to Use

Use this skill when the user asks to:

- query Gaia, RAVE, StarHorse, SHBoost, or another astronomy catalog;
- access data from S3/object storage or `data.aip.de`;
- read large Parquet/HDF5 datasets for astronomy analysis;
- generate CMD, RA/Dec, Galactic, or density plots from catalog data;
- decide whether a task should run locally or on REANA;
- clean up fragmented astronomy data-access workflows.

For already-known narrow tasks, route directly using the table below.

## Routing Table

| User intent | Canonical skill | Default execution |
|---|---|---|
| Generic TAP/ADQL catalog query | `tap-pyvo-adql-access` | local smoke query, then REANA for full task |
| Gaia@AIP TAP or Daiquiri REST | `gaia-aip-data-access` | local endpoint probe, then REANA if producing results |
| RAVE DR6 query or plot | `rave-dr6-data-access` | local TOP 1/TOP 100 probe, then plot/cache |
| Public S3/Parquet catalog | `s3-parquet-astro-access` | local metadata/column probe, REANA for full computation |
| SHBoost public S3 CMD | `s3-parquet-astro-access` + `astro-catalog-plotting-cache` | REANA if producing final result |
| StarHorse local data | `starhorse-access` + `astro-catalog-plotting-cache` | local on Newton/relevant host unless user requests REANA |
| Final plot from catalog data | `astro-catalog-plotting-cache` | local or REANA depending on data size and reproducibility need |
| User says “run task” | `reana-operator` | REANA task-first path |

## Standard Procedure

1. **Classify access path.** Decide TAP/pyvo, Gaia REST, S3/Parquet, local file, or hybrid.
2. **Run a minimal probe.** Use `TOP 1`, metadata read, or selected columns only. Do not start with full-catalog reads.
3. **Capture provenance.** Record endpoint, query, columns, filters, timestamp, and software versions.
4. **Cache deliberately.** Store small query outputs as CSV preview and reusable outputs as Parquet.
5. **Choose execution.** If the user task is a real computational result, create a REANA task via `reana-operator`; use local only for probes and inspection.
6. **Plot with conventions.** Use white background, hexbin/density for large stellar catalogs, NaN filtering, and publication-ready labels.
7. **Verify outputs.** Read back the cache or inspect plot dimensions/file existence before reporting success.

## Minimal Decision Checklist

Ask only if the answer changes execution. Otherwise use defaults.

- Catalog/source known? If not, search skill inventory or web docs.
- Need a few rows or a final analysis product? Probe locally; final product on REANA.
- Data volume large? Use column projection and Dask/Datashader.
- Credentials involved? Keep in environment variables; never commit them.
- Plot requested? Apply `astro-catalog-plotting-cache` conventions.

## Canonical Cache Layout

```text
outputs/<task-name>/
  query.adql                 # or query.sql / source_uri.txt
  provenance.yaml
  preview.csv
  data.parquet
  figure.png
```

`provenance.yaml` should include:

```yaml
source: gaia.aip.de/tap
access_method: tap-adql
query_file: query.adql
created_utc: "YYYY-MM-DDTHH:MM:SSZ"
columns: [source_id, ra, dec]
row_count: 100
software: {python: "3.x", pyvo: "...", pandas: "..."}
```

## REANA Default

For user-facing computational tasks:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py task \
  --project /tmp/<task> \
  --task "<short description>" \
  --script analysis.py \
  --output figure.png \
  --environment-profile astro-ml \
  --run --timestamp
```

Use `--package <name>` for packages not modeled as available in the selected REANA environment.

## Common Pitfalls

1. **Starting with full-catalog reads.** Always run a tiny probe first.
2. **Mixing access and plotting logic.** Cache data first, plot second.
3. **Using SQL `LIMIT` in ADQL.** TAP/ADQL uses `TOP N`; some services reject `LIMIT`.
4. **Assuming S3 paths are public.** Test anonymous access and endpoint URL first.
5. **Forgetting provenance.** Without query/endpoint/columns, plots are not reproducible.
6. **Running final scientific tasks only locally.** For reproducible deliverables, prefer REANA.
7. **Dense scatter plots.** Use hexbin or Datashader for stellar-density plots.

## Verification Checklist

- [ ] Access method selected and named.
- [ ] Minimal probe completed or failure classified.
- [ ] Query/source URI saved.
- [ ] Cache path and row count verified.
- [ ] Plot conventions applied if a figure was requested.
- [ ] REANA used for executable result tasks when appropriate.
- [ ] No tokens or private paths committed.
