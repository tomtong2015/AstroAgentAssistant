---
name: gaia-aip-data-access
description: Use when accessing Gaia data through AIP services, choosing between Gaia@AIP TAP/ADQL/pyvo and Daiquiri REST/PostgreSQL APIs, handling CSRF/queue details, checking endpoint health, caching results, and falling back when services are unavailable.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [astronomy, gaia, aip, tap, adql, daiquiri, postgres]
    related_skills: [astro-data-access-umbrella, tap-pyvo-adql-access, astro-catalog-plotting-cache]
---

# Gaia@AIP Data Access

## Overview

This is the Gaia-specific access skill. It separates the two AIP paths that are often conflated:

1. **TAP/ADQL/pyvo** — normal catalog selections and interoperable astronomy workflows.
2. **Daiquiri REST/PostgreSQL API** — AIP web-query backend, queue-controlled jobs, metadata, and JSON rows.

Use a tiny endpoint probe before any full task. Gaia services can be affected by migration/outage windows; classify failures instead of treating every error as an ADQL problem.

## When to Use

Use this skill when the user asks to:

- query Gaia DR3 at AIP;
- choose between Gaia TAP and the AIP query API;
- access `gaiadr3.gaia_source`;
- fetch Gaia metadata/columns;
- run Gaia query jobs with Daiquiri queues;
- build Gaia CMD/RA-Dec plots with reproducible caches.

## Endpoints

| Purpose | Endpoint | Query language |
|---|---|---|
| TAP service | `https://gaia.aip.de/tap/` | ADQL |
| Daiquiri query API | `https://gaia.aip.de/query/api/jobs/` | PostgreSQL |
| metadata | `https://gaia.aip.de/metadata/gaiadr3/gaia_source/` | HTTP/HTML/JSON-like page |

## Recommended Path

Use TAP first for normal catalog work:

```python
import pyvo
service = pyvo.dal.TAPService("https://gaia.aip.de/tap/")
query = """
SELECT TOP 100 source_id, ra, dec, l, b, parallax, phot_g_mean_mag, bp_rp
FROM gaiadr3.gaia_source
WHERE parallax > 0
ORDER BY parallax DESC
"""
df = service.run_sync(query).to_table().to_pandas()
```

Use Daiquiri REST when you specifically need the AIP query API, PostgreSQL syntax, queues, or JSON row fetching.

## Daiquiri REST Pattern

```bash
COOKIE=/tmp/gaia_cookies.txt
curl -s -c "$COOKIE" "https://gaia.aip.de/query//sql/" > /dev/null
CSRF=$(grep csrftoken "$COOKIE" | awk '{print $7}')

curl -s -b "$COOKIE" -c "$COOKIE" \
  -X POST \
  -H "Referer: https://gaia.aip.de/query//sql/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{"query":"SELECT COUNT(*) FROM gaiadr3.gaia_source","query_language":"postgresql","queue":"5m"}' \
  "https://gaia.aip.de/query/api/jobs/"
```

Queue names:

| UI meaning | API value |
|---|---|
| default / 30 seconds | omit `queue` |
| 5 minutes | `5m` |
| 2 hours | `2h` |

Poll:

```bash
curl -s -b "$COOKIE" -c "$COOKIE" \
  -H "Referer: https://gaia.aip.de/query/$JOB_ID/" \
  -H "X-CSRFToken: $CSRF" \
  -H "X-Requested-With: XMLHttpRequest" \
  "https://gaia.aip.de/query/api/jobs/$JOB_ID/"
```

Rows:

```bash
curl -s -b "$COOKIE" -c "$COOKIE" \
  -H "Referer: https://gaia.aip.de/query/$JOB_ID/" \
  -H "X-CSRFToken: $CSRF" \
  -H "X-Requested-With: XMLHttpRequest" \
  "https://gaia.aip.de/query/api/jobs/$JOB_ID/rows/?limit=10&offset=0"
```

## Common Gaia Columns

| Column | Meaning |
|---|---|
| `source_id` | Gaia source identifier |
| `ra`, `dec` | ICRS position in degrees |
| `l`, `b` | Galactic longitude/latitude |
| `parallax`, `parallax_error` | parallax and uncertainty |
| `phot_g_mean_mag` | G-band mean magnitude |
| `bp_rp` | BP-RP colour |
| `ruwe` | astrometric quality indicator |
| `radial_velocity` | RV where available |
| `teff_gspphot`, `logg_gspphot`, `mh_gspphot` | GSP-Phot stellar parameters |

## Health and Fallbacks

Run a small probe:

```sql
SELECT TOP 1 source_id FROM gaiadr3.gaia_source
```

If AIP TAP returns 403/404, zero rows for trivial probes, or migration notices:

1. report Gaia@AIP as temporarily unavailable;
2. try ESA Gaia Archive only if the task can tolerate endpoint differences;
3. for plotting demos, use cached/mock data and label it clearly;
4. do not fabricate Gaia query results.

## Caching and Plotting

Save:

```text
query.adql
preview.csv
data.parquet
provenance.yaml
```

Then use `astro-catalog-plotting-cache` for figures. For CMDs, filter NaNs and invert magnitude axis.

## Common Pitfalls

1. **Confusing APIs.** TAP uses ADQL; Daiquiri API uses PostgreSQL.
2. **Using TAP `/query/tap/...` as JSON.** It may return HTML; use the documented endpoints.
3. **Wrong queue names.** Use `5m` or `2h`, not the UI label string.
4. **No CSRF headers.** Daiquiri API requires cookie, `X-CSRFToken`, `Referer`, and `X-Requested-With`.
5. **Using `LIMIT` in ADQL.** Use `TOP N` for TAP.
6. **Ignoring outage/migration.** Run health probes and state uncertainty.

## Verification Checklist

- [ ] Endpoint probe run and result/failure classified.
- [ ] Correct query language used for the chosen endpoint.
- [ ] Exact query saved.
- [ ] Result cached to Parquet or JSON/CSV preview.
- [ ] Provenance records endpoint, row count, columns, queue if any.
- [ ] Fallback clearly labeled if AIP endpoint is unavailable.
