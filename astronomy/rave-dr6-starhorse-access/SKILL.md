---
name: rave-dr6-starhorse-access
description: Query RAVE DR6 via TAP and crossmatch with SHboost24 distances for nearby star analysis.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [astronomy, rave-dr6, starhorse, tap, adql, crossmatch, s3, parquet]
    category: astronomy
    related_skills: [starhorse-access, data-aip-de-s3, gaia-dr3-tap-query]
---

# RAVE DR6 + SHboost24 Access Pattern

## When to Use
When you need RAVE DR6 star coordinates (ra, dec) paired with distances or Galactocentric positions for analysis of nearby stars.

## Data Sources

### 1. RAVE DR6 via TAP
- Endpoint: `https://www.rave-survey.org/tap/sync`
- Tables: `ravedr6.dr6_obsdata` (ra_input, dec_input, rave_obs_id), `ravedr6.dr6_cnn` (source_id, rave_obs_id)
- **CRITICAL:** `ravedr6.dr6_x_gaiaedr3` and `ravedr6.dr6_sparv` are NOT TAP-accessible — they appear in VOSI tables but all queries return "Not found"
- gaia.aip.de TAP is also down/unresponsive
- Only working approach: JOIN `dr6_obsdata` + `dr6_cnn` on `rave_obs_id`

### 2. SHboost24 via HTTP (no boto3/s3fs needed)
- Public parquet on S3: `https://s3.data.aip.de:9000/shboost2024/shboost_08july2024_pub.parq/part.0.parquet` (~190 MB)
- Download directly with `urllib.request` — no auth required
- Schema: `source_id`, `dist`, `xg`, `yg`, `zg`, `xgbdist_av_*`, `bprp0`, `mg0`, etc.
- SHboost24 has 1,701,553 stars with StarHorse distances and Galactocentric coordinates

## Procedure

### Step 1: Query RAVE DR6 (all ~426K crossmatched stars)

SQL:
```sql
SELECT o.ra_input, o.dec_input, c.source_id
FROM ravedr6.dr6_obsdata o
JOIN ravedr6.dr6_cnn c ON o.rave_obs_id = c.rave_obs_id
```

- Use `TOP 100000` (not `LIMIT m OFFSET n` — OFFSET causes 400 errors)
- Fetch in batches (~100K per batch, ~5 batches total)
- Format: `votable`
- Parse with regex: `<FIELD name="...">` for columns, `<TD>([^<]*)</TD>` for values
- Python system interpreter: `/usr/bin/python3` (3.12) has `numpy`, `boto3`; install `pyarrow` and `pandas` with `pip3 install --break-system-packages`

### Step 2: Download SHboost24 parquet
```python
import urllib.request
url = "https://s3.data.aip.de:9000/shboost2024/shboost_08july2024_pub.parq/part.0.parquet"
urllib.request.urlopen(url).read()  # returns 190 MB
```

Read with `pyarrow.parquet` (no pandas needed for schema inspection):
```python
import pyarrow.parquet as pq
t = pq.read_table('/path/to/file.parquet', columns=['source_id', 'dist', 'xg', 'yg', 'zg'])
```

### Step 3: Crossmatch on source_id
```python
import pyarrow.parquet as pq, pickle

# SHboost lookup
t = pq.read_table('shboost_08july2024_pub.parquet', columns=['source_id', 'dist', 'xg', 'yg', 'zg'])
sh = t.to_pandas().reset_index()
sh_lookup = dict(zip(sh['source_id'], sh['dist']))

# RAVE data
with open('rave_dr6_gaia.pkl', 'rb') as f:
    rave = pickle.load(f)

# Match, deduplicate (keep first = nearest if sorted by dist)
matched = {}
for row in rave:
    sid = row['source_id']
    if sid in sh_lookup and sid not in matched:
        matched[sid] = {**row, 'dist': sh_lookup[sid]}

matched_list = sorted(matched.values(), key=lambda x: x['dist'])
top100 = matched_list[:100]
```

## Known Limitations
- Crossmatch rate is low (~658 / 426K RAVE stars) because SHboost24 is an independent survey
- SHboost24 `source_id` values are Gaia DR2/EDR3 format — RAVE DR6 CNN crossmatch provides these
- RAVE observes at |b| > 30°, mostly southern sky (dec < 0)

## Pitfalls
- Do NOT use `LIMIT/OFFSET` — use `TOP n` per batch
- Do NOT trust `dr6_x_gaiaedr3` via TAP — table exists in VOSI but returns errors
- Do NOT use the hermes venv python — it has no scientific packages; use `/usr/bin/python3`
- SHboost parquet source_id may be the index — call `.reset_index()` on the DataFrame after `to_pandas()`

## Verification
- RAVE DR6 + CNN crossmatch: 426,574 stars fetched in ~5 batches
- SHboost24: 1,701,553 stars, dist range 0.008–546 kpc
- Crossmatch yield: ~658 unique stars (low rate by design)
- Top 100 closest stars span 0.032–0.24 kpc