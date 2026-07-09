# DRP Hub API — Session Test Results (2026-07-09)

## Test Summary

All 14 API endpoints tested and confirmed working with the `drp_pat_` JWT token.

## Test Results

| # | Endpoint | Method | Expected | Actual | Notes |
|---|----------|--------|----------|--------|-------|
| 1 | `/health` | GET | 200 OK | ✅ 200 | No auth required |
| 2 | `/config` | GET | 200 OK | ✅ 200 | Returns enums, rate limits, capabilities |
| 3 | `/products` | GET | 200 OK | ✅ 200 | Paginated, 18 total products, 3 categories |
| 4 | `/products?mine=true` | GET | 200 OK | ✅ 200 | 10 products owned by user |
| 5 | `/products?q=reana` | GET | 200 OK | ✅ 200 | 19 results for "reana" |
| 6 | `/products/{id}` | GET | 200 OK | ✅ 200 | Full product with all fields |
| 7 | `/products/{id}?include=links` | GET | 200 OK | ✅ 200 | HATEOAS links: self, maturity, lineage, clone, human-review, publish, audit, events |
| 8 | `/products/{id}/maturity` | GET | 200 OK | ✅ 200 | Gates + missing list for L1-L4 |
| 9 | `/products/{id}/lineage` | GET | 200 OK | ✅ 200 | Ancestors/children |
| 10 | `/products/{id}/audit` | GET | 200 OK | ✅ 200 | Audit log events |
| 11 | `/products` | POST | 201 Created | ✅ 201 | Create with dry_run=true first |
| 12 | `/products/{id}` | PATCH | 200 OK | ✅ 200 | Partial update, all fields optional |
| 13 | `/products/{id}/clone` | POST | 201 Created | ✅ 201 | Clone with dry_run=true first |
| 14 | `/products/{id}/publish` | POST | 422 (no L4) | ✅ 422 | Dry_run=200, real=422 without L4 gates |
| 14b | `/products/{id}` | DELETE | 204 No Content | ✅ 204 | Soft delete, sets deleted_at |
| 14c | `/products/{id}` | GET (deleted) | 404 | ✅ 404 | Verified deletion |
| 14d | `/products` | POST (bad body) | 400 | ✅ 400 | validation_error for empty title |
| 14e | `/products/{bad_id}` | GET | 404 | ✅ 404 | not_found |

## Key Observations

- **204 No Content** for DELETE — `resp.read().decode()` returns empty string, handle gracefully
- **422** for publish without L4 gates — returns `{"error": {"code": "validation_error", ...}}`
- **400** for create with empty title — returns `{"error": {"code": "validation_error", ...}}`
- **Dry run** always returns 200 with `{"dry_run": true, "projected": {...}}` — never writes
- **Idempotency-Key** header auto-generated per request — no conflict even with retries
- **Visibility filtering**: `?mine=true` shows only owned products; default shows public + own
- **HATEOAS links** only returned when `?include=links` is explicitly requested

## Test Products Created/Used

| ID | Title | Action | Result |
|----|-------|--------|--------|
| 23bb5450... | Halo Mass Distribution | READ + MATURITY | L1 passes, L2-L4 fail |
| fafd5c4b... | CERN Open Data Exercise | READ + LINEAGE | 0 ancestors, 1 child |
| 88d324bc... | DRP Hub Skill Test | CREATE → PATCH → DELETE | Clean lifecycle test |
| 10857656... | Test Clone | CLONE → PUBLISH | Publish fails without L4 |

## Environment Notes

- Token was written to `/tmp/drp_token_full.txt` and read at runtime to avoid tool truncation
- Config saved to `.hermes/config.yaml` env section
- No network issues — all requests completed in <2s
- Rate limit: 60/min GET, 20/min mutation (per actor per route)
