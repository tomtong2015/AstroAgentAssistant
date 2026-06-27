# RAVE DR6 nearest-100 stars REANA smoke test

Generated: 2026-06-27

## Purpose

Query the public RAVE DR6 TAP service, select the nearest 100 finite rows from the Gaia EDR3 cross-match by positive parallax, and produce a publication-style summary figure.

## Data access

- TAP endpoint: `https://www.rave-survey.org/tap/`
- Table: `ravedr6.dr6_x_gaiaedr3`
- Query file: [`query.adql`](query.adql)
- Method: synchronous TAP POST with `LANG=ADQL`, `FORMAT=votable`, parsed locally in Python.

## REANA workflow

- Backend: `https://reana-dev.kube.aip.de`
- Workflow: `rave-nearest100-plot-20260627-175725`
- Status: `finished`
- Environment: `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c`

## Output files

| File | Description |
|---|---|
| `rave_dr6_nearest100_summary.png` | Multi-panel summary plot. |
| `rave_dr6_nearest100.csv` | Tabular data used for plotting. |
| `rave_dr6_nearest100.parquet` | Parquet cache of plotted data. |
| `provenance.json` | Machine-readable provenance and caveats. |
| `query.adql` | Exact query text. |
| `rave_nearest_candidates.xml` | Raw TAP VOTable response for candidate rows. |

## Verified summary

- Rows plotted: 100
- Distance range: 8.216--20.685 pc
- Median distance: 17.317 pc
- RA range: 2.439--359.337 deg
- Dec range: -76.703--2.726 deg

## Caveats

- RAVE is a southern-hemisphere spectroscopic survey; this is not an all-sky-complete nearest-star sample.
- Distances use simple inverse parallax for visualization.
- Approximate absolute G magnitude uses Gaia EDR3 `phot_g_mean_mag` and parallax.
