---
name: reana-client-failover
description: >-
  Use when a REANA workflow operation needs a robust client launcher: prefer native reana-client when installed, automatically fall back to Dockerized reanahub/reana-client when native client is missing, verify Docker availability, preserve environment-based credentials, and run local workflow projects with correct native-vs-Docker paths.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [reana, docker, failover, client, workflow, reproducibility]
    category: reana-workflows
    related_skills: [reana-operator, reana-client-docker, reana-client-config, reana-workflow-best-practices]
---

# REANA Client Failover

## Overview

This skill provides a user-friendly failover layer for REANA client commands.

The rule is simple:

1. Prefer the native `reana-client` executable if it is installed.
2. If native `reana-client` is not installed, check whether Docker is available.
3. If Docker is available, run the Docker Hub image `reanahub/reana-client`.
4. If neither native client nor Docker is available, stop with a clear setup message.

The default image is:

```bash
reanahub/reana-client:0.95.0-alpha.3
```

Override it with:

```bash
export REANA_CLIENT_IMAGE="reanahub/reana-client:<tag>"
```

Docker Hub reference: <https://hub.docker.com/r/reanahub/reana-client>

Credentials are always expected in environment variables:

```bash
export REANA_SERVER_URL="https://reana-dev.kube.aip.de"
export REANA_ACCESS_TOKEN="..."
```

Never write `REANA_ACCESS_TOKEN` into `reana.yaml`, scripts, README files, commits, or logs.

## When to Use

Use this skill when the user asks any of the following:

- “Use REANA, but fall back to Docker if `reana-client` is not installed.”
- “Check whether the REANA client is available.”
- “Run REANA commands in a user-friendly way across machines.”
- “Make REANA commands work even on hosts without native `reana-client`.”
- “Use the Dockerized REANA client from Docker Hub.”
- “Diagnose why REANA commands cannot start.”

Prefer `reana-operator` for high-level workflow operations such as recent jobs, status, scaffolding, running, logs, and download. This failover skill is the lower-level client-selection layer used by the operator.

## Client Selection Policy

Default mode is automatic:

```bash
export REANA_CLIENT_MODE=auto
```

Supported modes:

| Mode | Behavior |
|---|---|
| `auto` | Prefer native `reana-client`; if missing, use Docker. |
| `native` | Require native `reana-client`; fail if missing. |
| `docker` | Force Dockerized `reanahub/reana-client`; fail if Docker unavailable. |

Recommended default:

```bash
unset REANA_CLIENT_MODE   # same as auto
```

Force Docker for testing or reproducibility:

```bash
export REANA_CLIENT_MODE=docker
```

Force native client when Docker must not be used:

```bash
export REANA_CLIENT_MODE=native
```

## Helper CLI

This skill ships a wrapper:

```bash
python reana-workflows/reana-client-failover/scripts/reana_client_auto.py doctor
python reana-workflows/reana-client-failover/scripts/reana_client_auto.py ping
python reana-workflows/reana-client-failover/scripts/reana_client_auto.py --project ./my-workflow run -w my-workflow -f reana.yaml
python reana-workflows/reana-client-failover/scripts/reana_client_auto.py list -v --json
```

Everything after the wrapper options is passed to `reana-client`.

### Doctor command

Use this first when debugging:

```bash
python reana-workflows/reana-client-failover/scripts/reana_client_auto.py doctor
```

It reports:

- selected mode: `native` or `docker`
- active `REANA_SERVER_URL`
- whether a token is configured, without printing it
- native `reana-client` path/version if present
- Docker path and daemon availability
- Docker image that will be used

### Running arbitrary REANA commands

Examples:

```bash
python reana-workflows/reana-client-failover/scripts/reana_client_auto.py ping
python reana-workflows/reana-client-failover/scripts/reana_client_auto.py status -w my-workflow
python reana-workflows/reana-client-failover/scripts/reana_client_auto.py logs -w my-workflow
python reana-workflows/reana-client-failover/scripts/reana_client_auto.py download -w my-workflow -o outputs/my-workflow
```

For local workflow submission, pass the project directory:

```bash
python reana-workflows/reana-client-failover/scripts/reana_client_auto.py \
  --project ./my-analysis \
  run -w my-analysis -f reana.yaml
```

The wrapper handles path semantics:

| Mode | Working directory / file path behavior |
|---|---|
| native | runs inside `./my-analysis`; uses `reana.yaml` |
| Docker | mounts `./my-analysis:/workspace`; uses `/workspace/reana.yaml` |

## Docker Pattern

When native `reana-client` is missing, the wrapper builds this pattern:

```bash
docker run --rm \
  -e REANA_SERVER_URL \
  -e REANA_ACCESS_TOKEN \
  -v "$PWD:/workspace" \
  -w /workspace \
  reanahub/reana-client:0.95.0-alpha.3 \
  run -w my-workflow -f /workspace/reana.yaml
```

For commands that do not need local files, it omits the project mount:

```bash
docker run --rm \
  -e REANA_SERVER_URL \
  -e REANA_ACCESS_TOKEN \
  reanahub/reana-client:0.95.0-alpha.3 \
  ping
```

## User-Friendly Failure Messages

Use clear failure classes:

| Problem | Message / fix |
|---|---|
| Missing `REANA_SERVER_URL` | Set `REANA_SERVER_URL` for the target backend. |
| Missing `REANA_ACCESS_TOKEN` | Set `REANA_ACCESS_TOKEN`; never paste it into files. |
| Native client missing and Docker missing | Install `reana-client` or Docker. |
| Docker command exists but daemon unavailable | Start Docker or fix permissions/group membership. |
| Docker image missing | Pull image or let Docker pull it automatically. |
| Project path missing | Pass `--project /path/to/project` or run from the workflow directory. |
| Native run uses `/workspace/reana.yaml` | Use local `reana.yaml`; `/workspace` is Docker-only. |

## Integration with `reana-operator`

`reana-operator` uses the same policy:

- `auto`: native first, Docker fallback
- `native`: require native client
- `docker`: force Docker

For high-level tasks, use:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py client
python reana-workflows/reana-operator/scripts/reana_operator.py backends
python reana-workflows/reana-operator/scripts/reana_operator.py recent --limit 5
python reana-workflows/reana-operator/scripts/reana_operator.py run --project ./my-analysis --workflow my-analysis --timestamp
```

## Common Pitfalls

1. **Assuming Docker reads `~/.reana/config.yaml`.** It does not by default. Pass `REANA_SERVER_URL` and `REANA_ACCESS_TOKEN` as environment variables.

2. **Using `/workspace/reana.yaml` with native `reana-client`.** `/workspace` only exists inside the Docker container. Native mode must run from the project directory and use `reana.yaml`.

3. **Forgetting `-w /workspace` in Docker mode.** Without the working directory, `reana-client` may upload from the wrong directory or miss input files.

4. **Leaking tokens in shell history.** Prefer exporting tokens once in the shell or reading from a protected config file. Do not include token values in commands committed to a repo.

5. **Docker permission errors.** If Docker exists but the daemon is not reachable, check `docker version`, group membership, and socket permissions. On some systems `sg docker -c '<command>'` can be used as a temporary workaround.

## Verification

Run these checks:

```bash
python reana-workflows/reana-client-failover/scripts/reana_client_auto.py doctor
python reana-workflows/reana-client-failover/scripts/reana_client_auto.py ping
REANA_CLIENT_MODE=docker python reana-workflows/reana-client-failover/scripts/reana_client_auto.py doctor
REANA_CLIENT_MODE=docker python reana-workflows/reana-client-failover/scripts/reana_client_auto.py ping
```

For project submission:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py scaffold \
  --project /tmp/reana-failover-smoke \
  --script analysis.py \
  --code 'open("output.txt", "w").write("hello from failover\\n")' \
  --output output.txt \
  --workflow reana-failover-smoke \
  --force

python reana-workflows/reana-operator/scripts/reana_operator.py validate --project /tmp/reana-failover-smoke
REANA_CLIENT_MODE=docker python reana-workflows/reana-operator/scripts/reana_operator.py run --project /tmp/reana-failover-smoke --workflow reana-failover-smoke --timestamp
```

Expected:

- `doctor` reports the selected client mode.
- Native mode works if `reana-client` is installed.
- Docker mode works if Docker is reachable.
- Token value is never printed.
- Project submission uses the correct path for the selected mode.
