---
name: rave-dr6-data-access
description: Use when querying, caching, or plotting RAVE DR6 data via its TAP/ADQL service, including Gaia cross-match tables, recent observations, stellar parameters, southern-sky coverage caveats, VOTable parsing, and publication-ready visualizations.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [astronomy, rave, tap, adql, catalog, stellar-parameters]
    related_skills: [astro-data-access-umbrella, tap-pyvo-adql-access, astro-catalog-plotting-cache]
---

# RAVE DR6 Data Access

## Overview

This is the canonical RAVE DR6 skill. It consolidates RAVE TAP querying, Gaia cross-match access, recent-observation queries, and plotting caveats. Use this before older RAVE plotting/animation examples.

## When to Use

Use this skill when the user asks to:

- query RAVE DR6;
- access RAVE stellar parameters, radial velocities, or Gaia cross-matches;
- find recent RAVE observations;
- plot RAVE RA/Dec, Galactic, or CMD-like views;
- explain RAVE southern-sky coverage bias.

## Endpoint and Key Tables

```text
TAP endpoint: https://www.rave-survey.org/tap/
```

| Table | Purpose |
|---|---|
| `ravedr6.dr6_x_gaiaedr3` | Gaia EDR3 cross-match: RA/Dec, parallax, G magnitude, BP-RP |
| `ravedr6.dr6_sparv` | stellar parameters: Teff, log g, metallicity, RV |
| `ravedr6.dr6_obsdata` | observations and dates |
| `ravedr6.dr6_orbits` | orbital parameters |

Do not use old `www.rave-aip.de`; it is not the canonical endpoint.

## Basic pyvo Query

```python
import pyvo
service = pyvo.dal.TAPService("https://www.rave-survey.org/tap/")
query = """
SELECT TOP 100 source_id, ra, dec, l, b, parallax, phot_g_mean_mag, bp_rp
FROM ravedr6.dr6_x_gaiaedr3
WHERE parallax > 0
ORDER BY parallax DESC
"""
df = service.run_sync(query).to_table().to_pandas()
```

## curl Fallback

```bash
curl -s -X POST 'https://www.rave-survey.org/tap/sync' \
  -d 'REQUEST=doQuery' \
  -d 'LANG=ADQL' \
  --data-urlencode 'QUERY=SELECT TOP 100 source_id,ra,dec,l,b,parallax,phot_g_mean_mag,bp_rp FROM ravedr6.dr6_x_gaiaedr3 WHERE parallax > 0 ORDER BY parallax DESC' \
  -d 'FORMAT=votable' \
  -o rave_dr6.xml
```

RAVE may return VOTable even when another format is requested; parse the response content rather than trusting the file extension. `LANG=ADQL` is required.

## Recent Observations

```sql
SELECT TOP 100 *
FROM ravedr6.dr6_obsdata
ORDER BY obs_start_date DESC
```

If a date column name differs, inspect `TAP_SCHEMA.columns` first.

## Coverage Caveat

RAVE is a southern-hemisphere survey. Plots will show strong sky-coverage bias. Always mention this when presenting RAVE all-sky or RA/Dec visualizations.

## Caching

```python
from pathlib import Path
out = Path("outputs/rave-dr6")
out.mkdir(parents=True, exist_ok=True)
df.to_parquet(out / "rave.parquet", index=False)
df.head(20).to_csv(out / "preview.csv", index=False)
(out / "query.adql").write_text(query)
```

Then hand off to `astro-catalog-plotting-cache`.

## Plotting Defaults

For nearest-star or cross-match plots:

- RA/Dec: small samples can use scatter, large samples should use density.
- Galactic projection: show Sun at origin if plotting unit vectors.
- CMD-like plots: use `bp_rp` vs `phot_g_mean_mag` or absolute magnitude only when distances/parallax treatment is explicit.
- Include RAVE coverage caveat in captions.

## REANA Pattern

For final products, create `analysis.py` and run:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py task \
  --project /tmp/rave-dr6-task \
  --task "query RAVE DR6 and plot" \
  --script analysis.py \
  --output rave.parquet \
  --output rave_plot.png \
  --environment-profile astro-ml \
  --package pyvo \
  --run --timestamp
```

## Common Pitfalls

1. **Missing `LANG=ADQL` in POST.** RAVE returns a field-required error.
2. **Wrong schema.** RAVE does not expose `gaiadr3.gaia_source`; use `ravedr6.*` tables.
3. **Using Gaia-specific assumptions.** RAVE tables and coverage differ.
4. **Overclaiming all-sky completeness.** RAVE has strong southern coverage bias.
5. **Large queries without TOP.** Keep probes modest.
6. **Rank slicing in ADQL.** TAP has no portable `OFFSET`; query TOP M then slice in pandas if needed.

## Verification Checklist

- [ ] TAP endpoint reachable with `SELECT TOP 1`.
- [ ] Query uses `ravedr6.*` table names.
- [ ] `LANG=ADQL` included for curl POST.
- [ ] Data cached to Parquet and preview CSV.
- [ ] Coverage caveat included in plot/report.
- [ ] Final task uses REANA when requested.
