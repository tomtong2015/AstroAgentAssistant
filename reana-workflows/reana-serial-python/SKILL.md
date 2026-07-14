---
name: reana-serial-python
description: When explicitly asked, use it to build a REANA serial workflow (Python analysis on remote data, Parquet cache, PNG outputs).
version: 1.1.0
author: AstroAgent / AIP
license: MIT
prerequisites:
  python:
    - pandas
    - matplotlib
    - pyarrow
    - pyvo
    - reana-client
metadata:
  hermes:
    tags: [reana, workflow, serial, python, parquet, analysis, reproducibility]
    category: workflows
    related_skills: [reana-aip, drphub-cards, docs-mcp-at-aip, s3-parquet-sampling, dask-hvplot-datashader-scientific-plots, cmd-plotting]
---

# REANA Serial Python Analysis Template

## When to Use
Use this skill when creating a REANA workflow that: (1) reads remote data (S3, HTTP, TAP), (2) processes it in Python, (3) caches intermediate results as Parquet, and (4) produces PNG outputs. All AIP REANA workflows use this pattern. The reana.yaml structure rules + approved environments live in **reana-aip** — load it alongside this skill.

## Procedure

### 1. Create a dedicated workflow directory
```bash
mkdir -p workflows/my-analysis && cd workflows/my-analysis
```

### 1a. REANA authentication
In DRP-Hub `drphub_service` sessions reana-client is already configured — verify with `reana-client ping`. Only if that fails, ask the user for their REANA token (do not guess a setup).

### 1b. Use Dask by default for huge S3/TAP inputs
If the remote input is large, prefer Dask over eager pandas loading and keep the effective working footprint around **32GB RAM**.

### 1c. Plan a local cache immediately
For data coming from **S3 or TAP**, cache the working dataset locally as Parquet before repeated downstream plotting or iteration.

### 2. Write `reana.yaml` (validated shape — see reana-aip for the structure rules)
```yaml
version: 0.9.0
inputs:
  files:
    - script.py
workflow:
  type: serial
  specification:
    steps:
      - name: analysis
        environment: 'gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c'
        kubernetes_memory_limit: '8Gi'
        commands:
          - python3 script.py
outputs:
  files:
    - output.png
    - cache.parquet
```
Notes: `inputs.files`/`outputs.files` are plain path lists; the per-step `environment:` has **no `docker://` prefix** and needs the `:5005` registry port; pick the environment from the approved table in **reana-aip** (`py311-astro-ml` shown here because Parquet needs pyarrow/s3fs; plain matplotlib-only jobs can use `py311-astro`). Raise `kubernetes_memory_limit` to `'32Gi'` for heavy data.

### 3. Write `script.py`
```python
import pandas as pd, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 1. Load / fetch remote data (or use cached Parquet)
df = pd.read_parquet('cache.parquet')  # if cached
# OR fetch from remote:
# import pyarrow.parquet as pq
# dataset = pq.ParquetDataset('s3://bucket/path/')
# df = dataset.read().to_pandas()

# 2. Analysis / plotting
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df['column'], bins=50)
fig.savefig('output.png')
df[['col_a', 'col_b']].to_parquet('cache.parquet', index=False)
```

### 4. VALIDATE, then run via reana-client
```bash
reana-client validate -f reana.yaml     # MANDATORY — all three checks must pass
reana-client run -w my-analysis         # create + upload + start
```
(reana-client write operations raise an approval card in the chat UI — expected.)

### 5. Monitor
```bash
reana-client status -w my-analysis
reana-client logs -w my-analysis | tail -50   # on failure
reana-client download -w my-analysis
```

## AIP Conventions
- Use approved environments only — the current list is in **reana-aip** (source: `https://gitlab-p4n.aip.de/punch_public/reana/environments`).
- Set `kubernetes_memory_limit` explicitly per step: `'8Gi'` small, `'32Gi'` heavy.
- Include all Python scripts in `inputs.files` (do not inline scripts in `reana.yaml`).
- Prefer `reana-client run -w <name>` over separate `upload` + `start`.
- For huge S3/TAP-derived tabular inputs, prefer Dask and materialize a local Parquet cache inside the workflow.
- Prefer `hvplot` for scientific plotting; for dense large-data plots use Dask + hvPlot + Datashader.

## Common Remote Data Patterns

| Source | Library | Example |
|---|---|---|
| S3 bucket | `pyarrow` | `pq.ParquetDataset('s3://bucket/path/')` |
| TAP service | `pyvo` | `tap.run_sync("SELECT ...")` |
| HTTP URL | `pandas` | `pd.read_csv('https://...')` |

## Pitfalls
- Do NOT invent custom environments — use only AIP-approved ones (reana-aip table).
- Do NOT omit scripts from workflow inputs — they must be listed in `inputs.files`.
- Do NOT skip `reana-client validate` — an invalid reana.yaml wastes a submit cycle (or ships a broken DRP card).
- Do NOT set memory below 8GB for large-parquet workflows — parquet loading is memory-intensive.

## Verification
- `reana-client validate -f reana.yaml` passes all three checks.
- `reana.yaml` references an approved environment.
- `reana-client status -w <name>` reaches `finished`.
- Output files exist and are PNG (unless PDF explicitly requested).
- Cached Parquet is saved in the workflow directory.
