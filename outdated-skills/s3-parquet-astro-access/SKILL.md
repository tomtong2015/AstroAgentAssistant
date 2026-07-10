---
name: s3-parquet-astro-access
description: Use when astronomy data lives in public or S3-compatible object storage as Parquet/HDF5/FITS-like products and the task needs endpoint probing, anonymous/credentialed access, Dask-first reads, local caching, column projection, sampling, or REANA-safe workflows.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [astronomy, s3, parquet, dask, cache, object-storage]
    related_skills: [astro-data-access-umbrella, astro-catalog-plotting-cache, reana-operator, data-aip-de-s3]
---

# S3 / Parquet Astronomy Access

## Overview

This is the canonical pattern for astronomy datasets stored in S3-compatible object storage, especially large Parquet catalogs. It favors metadata probes, column projection, Dask-first reads, local Parquet caches, and REANA-compatible scripts.

## When to Use

Use this skill when the user asks to:

- access `s3://...` astronomy data;
- read public SHBoost or other object-store catalogs;
- use `data.aip.de` / S3-compatible endpoints;
- sample or reduce massive Parquet datasets;
- cache remote catalog subsets locally;
- prepare a REANA job that reads S3/Parquet data.

## Access Patterns

| Data shape | Preferred tool | Notes |
|---|---|---|
| many Parquet files | Dask dataframe | column projection and lazy filtering |
| one medium Parquet file | pandas/pyarrow | read selected columns only |
| HDF5 on S3 | local cache first | HDF5 random access over S3 is fragile |
| final figure task | REANA | use `reana-operator task` with script and outputs |

## Procedure

### 1. Probe object-store access

Do not start by reading all rows. First check metadata/path reachability.

```python
import fsspec

url = "s3://bucket/path/"
storage_options = {"anon": True}
fs, path = fsspec.core.url_to_fs(url, **storage_options)
print(fs.ls(path)[:5])
```

For AIP S3-compatible endpoints:

```python
storage_options = {
    "anon": True,
    "client_kwargs": {"endpoint_url": "https://s3.data.aip.de:9000"},
}
```

Use credentials only through environment variables or protected config. Never commit keys.

### 2. Read selected columns with Dask

```python
import dask.dataframe as dd

columns = ["bprp0", "mg0"]
ddf = dd.read_parquet(
    "s3://bucket/path/*.parquet",
    columns=columns,
    storage_options=storage_options,
)
print(ddf.head())
```

### 3. Filter and sample before computing

```python
subset = ddf[columns].dropna()
sample = subset.sample(frac=0.01, random_state=42).compute()
sample.to_parquet("cache/sample.parquet", index=False)
```

For very large data, prefer aggregating directly with Datashader rather than materializing rows.

### 4. Cache and record provenance

```python
from pathlib import Path
import datetime, yaml

out = Path("outputs/s3-task")
out.mkdir(parents=True, exist_ok=True)
sample.to_parquet(out / "sample.parquet", index=False)
(out / "source_uri.txt").write_text("s3://bucket/path/*.parquet\n")
(out / "provenance.yaml").write_text(yaml.safe_dump({
    "access_method": "s3-parquet",
    "source_uri": "s3://bucket/path/*.parquet",
    "created_utc": datetime.datetime.utcnow().isoformat() + "Z",
    "columns": columns,
    "row_count": int(len(sample)),
}, sort_keys=False))
```

## REANA Pattern

For final computations or figures, make an external script and submit with the task-first operator:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py task \
  --project /tmp/s3-parquet-task \
  --task "read S3 parquet and create CMD" \
  --script analysis.py \
  --output cmd.png \
  --output sample.parquet \
  --environment-profile astro-ml \
  --run --timestamp
```

If needed:

```bash
--package s3fs --package dask --package pyarrow
```

The modeled `astro-ml` profile includes common packages such as Dask, fsspec, s3fs, pyarrow, pandas, numpy, matplotlib, and Datashader-adjacent plotting dependencies may still need verification.

## Plotting Handoff

For CMD, RA/Dec, or density plots, hand off the cached dataframe to `astro-catalog-plotting-cache`.

Default stellar-density conventions:

- white background;
- filter NaNs before plotting;
- use hexbin or Datashader for dense catalogs;
- invert magnitude axis;
- save high-DPI PNG and provenance.

## Common Pitfalls

1. **Reading full S3 datasets into pandas.** Use Dask and column projection first.
2. **No endpoint URL for S3-compatible storage.** Public AIP object storage may require `client_kwargs.endpoint_url`.
3. **HDF5 random reads over S3.** Cache HDF5 locally before repeated access.
4. **Credentials in code.** Use environment variables or configured credential stores only.
5. **Sampling before filtering.** Filter invalid rows/NaNs first when possible.
6. **Unbounded `compute()`.** Inspect partitions and use small samples before full aggregation.
7. **Missing provenance.** Save source URI, columns, filters, and sampling fraction.

## Verification Checklist

- [ ] `fs.ls` or metadata probe succeeds.
- [ ] Read uses explicit columns.
- [ ] Sample/cache file exists and can be read back.
- [ ] Provenance records URI, columns, filters, sample fraction.
- [ ] Final task runs on REANA when requested.
- [ ] Plotting uses `astro-catalog-plotting-cache` conventions.
