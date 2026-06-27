# Astronomy Skills Guide

This directory contains AIP/AstroAgent-developed astronomy skills. The skills are intentionally split into **canonical entry points** and **dataset-specific examples**.

For new work, start with the canonical entry point below, then route to a specialized skill only when the dataset or access method is known.

## Recommended Routing

```text
User astronomy/data task
  -> astro-data-access-umbrella
      -> tap-pyvo-adql-access         # generic TAP/ADQL/pyvo/curl
      -> gaia-aip-data-access         # Gaia@AIP TAP or Daiquiri REST/PostgreSQL
      -> rave-dr6-data-access         # RAVE DR6 TAP/data products
      -> s3-parquet-astro-access      # S3/object storage, Parquet, HDF5-style cache
      -> starhorse-access             # local StarHorse conventions
      -> astro-catalog-plotting-cache # CMD/sky maps/provenance/Datashader
      -> reana-operator               # when task should run on REANA
```

## Quick Decision Table

| User asks for | Start with | Then use |
|---|---|---|
| “Get catalog data” | `astro-data-access-umbrella` | Method-specific skill below |
| “Query TAP / ADQL / pyvo” | `tap-pyvo-adql-access` | `gaia-aip-data-access` or `rave-dr6-data-access` if dataset-specific |
| “Gaia at AIP” | `gaia-aip-data-access` | `tap-pyvo-adql-access` for TAP details; Daiquiri notes for REST jobs |
| “RAVE DR6” | `rave-dr6-data-access` | RAVE example skills for plots/animations |
| “S3 / Parquet / data.aip.de” | `s3-parquet-astro-access` | `data-aip-de-s3`, SHBoost examples |
| “Plot a CMD / density plot” | `astro-catalog-plotting-cache` | dataset-specific examples if needed |
| “Run the analysis task reproducibly” | `reana-operator` | Use `reana-operator task` with generated `reana.yaml` |
| “StarHorse local data” | `starhorse-access` | plotting/cache skill for figures |

## Grouped Skill Map

### 1. Canonical Entry Points

These are the preferred skills for new work.

| Skill | Purpose |
|---|---|
| `astro-data-access-umbrella` | Main decision layer: choose TAP, Gaia, RAVE, S3/Parquet, local data, plotting/cache, or REANA. |
| `tap-pyvo-adql-access` | Generic TAP/ADQL/pyvo/curl access pattern, VOTable handling, Parquet caching. |
| `s3-parquet-astro-access` | S3-compatible object storage, Parquet/HDF5-style access, Dask-first reads, local cache. |
| `astro-catalog-plotting-cache` | Publication-ready plots, white backgrounds, hexbin/density, Datashader, provenance. |

### 2. Gaia / Gaia@AIP

| Skill | Purpose | Status |
|---|---|---|
| `gaia-aip-data-access` | Canonical Gaia@AIP routing: TAP/ADQL vs Daiquiri REST/PostgreSQL. | canonical |
| `gaia-aip-de-adql` | Gaia ADQL/TAP query examples. | example |
| `gaia-dr3-tap-query` | Nearest-100 Gaia DR3 TAP query, cache, RA/Dec and Galactic plots. | example |
| `gaia-dr3-plot-with-dust` | Gaia nearest-stars figure with dust-map overlay. | example |
| `gaiadr3-aip-de-adql` | Gaia DR3 Daiquiri REST/PostgreSQL workflow. | example/reference |
| `gaiadr3-aip-query-api` | Similar Daiquiri REST API workflow. | example/reference |

**Refinement note:** prefer `gaia-aip-data-access` for new work; keep older Gaia skills as concrete worked examples until they are merged or rewritten.

### 3. RAVE DR6

| Skill | Purpose | Status |
|---|---|---|
| `rave-dr6-data-access` | Canonical RAVE DR6 TAP/query/cache/plot skill. | canonical |
| `rave-dr6` | General RAVE DR6 TAP and plotting recipes. | reference |
| `rave-dr6-tap-query` | pyvo TAP pattern for RAVE. | example |
| `rave-dr6-nearest-100-plot` | Nearest 100 RAVE stars; Galactic and RA/Dec plots. | example |
| `rave-dr6-recent-observations-plot` | Recent `dr6_obsdata` entries and RA/Dec plot. | example |
| `rave-dr6-public-talk-visualizations` | Presentation-style RAVE visualizations. | example |
| `rave-dr6-3d-animation` | RAVE nearest-stars 3D animation workflow. | example |
| `rave-dr6-3d-public-animation` | Public-talk 3D animation variant. | example |

**Live probe note:** RAVE TAP responded successfully to a `SELECT TOP 1 source_id,ra,dec FROM ravedr6.dr6_x_gaiaedr3` curl probe. It may return VOTable even when another format is requested.

### 4. S3 / Object Storage / Large Parquet Catalogs

| Skill | Purpose | Status |
|---|---|---|
| `s3-parquet-astro-access` | Canonical S3/Parquet/Dask/local-cache access. | canonical |
| `data-aip-de-s3` | AIP `data.aip.de` S3-backed datasets. | AIP-specific reference |
| `shboost-plot-s3` | Plot sampled SHBoost 2024 data from public S3. | example |
| `shboost-public-s3-cmd-plot` | SHBoost S3 CMD plot with REANA-friendly serial workflow. | example |

### 5. SHBoost / CMD / Stellar-Population Plots

| Skill | Purpose | Status |
|---|---|---|
| `shboost24-cmd` | Canonical SHBoost24 CMD skill with caching and plotting conventions. | canonical dataset skill |
| `shboost-cmd-plot` | ~100k-star SHBoost CMD from S3. | example |
| `shboost-cmd-visualization` | High-resolution density CMD with labels and GIF animation. | example |
| `shboost_cmd_plot_and_animation` | CMD PNG + MP4 animation workflow. | example |
| `shboost_full_cmd_datashader` | Full-dataset SHBoost CMD with Dask + Datashader. | example |
| `astro-catalog-plotting-cache` | Shared plotting/cache conventions. | canonical plotting layer |

### 6. StarHorse / Local Astronomy Datasets

| Skill | Purpose | Status |
|---|---|---|
| `starhorse-access` | Local StarHorse datasets and usage conventions. | canonical dataset skill |

Use `astro-catalog-plotting-cache` for StarHorse figures unless the task is only data discovery.

### 7. Visualization / Presentation / Animation

| Skill | Purpose |
|---|---|
| `astro-catalog-plotting-cache` | Canonical plotting/cache/provenance layer. |
| `gaia-dr3-plot-with-dust` | Gaia + dust-map figure. |
| `rave-dr6-public-talk-visualizations` | Public-talk RAVE plots. |
| `rave-dr6-3d-animation` | RAVE 3D animation. |
| `rave-dr6-3d-public-animation` | Public-talk RAVE 3D animation. |
| `shboost-cmd-visualization` | SHBoost CMD with labels and GIF. |
| `shboost_cmd_plot_and_animation` | SHBoost CMD PNG + MP4. |
| `shboost_full_cmd_datashader` | Full-dataset Datashader CMD. |

## Canonical vs Example Skills

- **Canonical skills** define reusable workflows and should be loaded first.
- **Example/reference skills** preserve concrete successful workflows and dataset-specific details.
- Do not delete example skills just because they overlap; consolidate only after the canonical skill contains the useful details and tests.

## Plotting Defaults

For astronomy plots, prefer:

- white background
- publication-ready labels and captions
- hexbin or density plots for large point clouds
- NaN filtering before plotting
- local cache + provenance JSON/Markdown
- REANA execution for reproducible computational tasks

## REANA Rule

If the user asks for an executable scientific task, prefer running it through:

```text
reana-workflows/reana-operator
```

Typical path:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py task \
  --project /tmp/my-astro-task \
  --task "short task description" \
  --script analysis.py \
  --output output.png \
  --environment-profile astro-ml \
  --run --timestamp
```

Use `s3-parquet-astro-access`, `tap-pyvo-adql-access`, or dataset-specific skills to write the task script, then let `reana-operator` generate and submit the `reana.yaml`.

## Maintenance Notes

When adding a new astronomy skill:

1. Decide whether it is **canonical** or an **example**.
2. If example, add `## Canonical Routing` pointing to the relevant canonical skills.
3. Update this README group map.
4. Regenerate the root README inventory.
5. Run the repo audit and focused secret scan before committing.
