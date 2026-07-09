# DRP Hub REST API — Complete Reference

**Base URL:** `https://drp-term.kube.aip.de/api/v1`
**OpenAPI spec:** `https://drphub-p4n.aip.de/api/v1/openapi.json`
**Swagger UI:** `https://drp-term.kube.aip.de/api/v1/docs#/`

## Auth Modes

| Mode | Header | Extra Header | Notes |
|------|--------|-------------|-------|
| User JWT | `Authorization: Bearer <token>` | — | Supabase or Keycloak JWT |
| Hermes Service Token | `Authorization: Bearer <token>` | `X-Acting-User-Id: <uuid>` | Agent acts on behalf of user |

All mutating endpoints accept optional `Idempotency-Key` header (client UUID, unique per actor+route+body, 86400s TTL).

## Endpoints

### `GET /health` — Liveness + DB probe
No auth required. Returns `{"status": "ok", "api_version": "v1", "db": true}`.

### `GET /config` — API capabilities
Returns API metadata: supported auth modes, maturity levels (0-4), enum values, rate limits, capabilities (etag, projection, HATEOAS, SSE, dry_run), deferred endpoints (phase-D: artifacts, versions, validation-runs, ai-jobs).

### `GET /products` — List products
**Query params:** `limit` (1-200, default 50), `cursor` (opaque base64url token), `q` (case-insensitive substring), `q_in` (`title` or `all`), `fields` (comma-separated projection), `include` (`links` for HATEOAS), `visibility` (`private`/`internal`/`shared`/`public`), `mine` (boolean).

**Visibility rules:** Default shows public + own products. With `mine=true` shows only own products (any visibility).

**Response:** `{ "items": [...], "next_cursor": "..." }`

### `POST /products` — Create product
**All fields required:** title, description, category, tags, visibility, source_type, git_url, git_branch, git_commit, entry_command, workflow_file, license, citation_cff_url, release_tag, env_image, env_image_digest, authors_orcid, reproducibility_depth, validation_scope, provenance_url, expected_outputs, has_s3, has_hpc, has_reana.

### `GET /products/{id}` — Get single product
**Query params:** `fields`, `include` (HATEOAS links), `If-None-Match` (etag).

### `PATCH /products/{id}` — Update product
Owner or admin only. All fields optional. Supports `?dry_run=true`. Requires `If-Match` header (etag).

### `DELETE /products/{id}` — Soft-delete
Returns 204 No Content. Sets `deleted_at` timestamp.

### `POST /products/{id}/clone` — Deep clone
**Body:** `title` (new title), `clone_mode` (`metadata_only`/`template`/`snapshot`/`fork`). Supports `?dry_run=true` (returns projected product). Resets validation, DOI, human-review on clone.

### `GET /products/{id}/maturity` — Maturity assessment
Returns `level` (0-4), `override` (manual), `gates` (`{l1Ok, l2Ok, l3Ok, l4Ok}`), `missing` (`{L1: [...], L2: [...], L3: [...], L4: [...]}`).

### `POST /products/{id}/publish` — Publish product
Requires L4 gates passing. Supports `?dry_run=true`. Returns updated product with status="published".

### `POST /products/{id}/human-review` — Mark human-reviewed
JWT only (rejects service tokens).

### `GET /products/{id}/lineage` — Clone ancestry
Returns `ancestors` (parents) and `children` (clones).

### `GET /products/{id}/audit` — Audit log
Owner or admin only. Supports `limit` and `cursor`. Returns events with `action`, `actor_user_id`, `acting_service`, `before`/`after` snapshots.

### `GET /products/{id}/events` — SSE audit stream
Long-lived `text/event-stream`. Heartbeat every 15s, caps at 5 minutes. Clients should reconnect.

### `GET /tools.json` — AI function descriptors
OpenAI/Anthropic function-call schemas with safety/approval flags under `x-drp`.

## Product Schema

**Enum values:**
- `visibility`: private, internal, shared, public
- `product_status`: draft, generated, validating, validated, failed_validation, human_reviewed, published, archived
- `source_type`: manual, repo, clone, template, ai_generated, imported
- `reproducibility_depth`: D0, D1, D2, D3, D4
- `validation_status`: not_validated, pending, running, passed, failed, waived
- `clone_mode`: metadata_only, template, snapshot, fork

**Key fields:** id, owner_user_id, title, description, avatar, category, tags, git_url, git_branch, git_commit, entry_command, workflow_file, license, citation_cff_url, release_tag, env_image, env_image_digest, authors_orcid, maturity_level, maturity_override, reproducibility_depth, validation_status, validation_scope, provenance_url, expected_outputs, has_s3, has_hpc, has_reana, human_reviewed, human_reviewed_by, human_reviewed_at, doi, archive_url, harvest_endpoint, oai_published, published_at, cloned_from_product_id, root_product_id, clone_mode, clone_count, run_count, likes, created_at, updated_at, computed_maturity_level, maturity_gates, maturity_missing.

## Rate Limits

- GET: 60/min per actor per route
- Mutation: 20/min per actor per route

## Key Patterns

- Use `?fields=` to keep responses small for LLM context windows
- Use `?include=links` for HATEOAS navigation
- Use `?dry_run=true` on PATCH/clone/publish to validate without writing
- Use SSE `/products/{id}/events` instead of polling `/audit`
- Bootstrap agents from GET `/tools.json` — ships OpenAI/Anthropic function-call descriptors
