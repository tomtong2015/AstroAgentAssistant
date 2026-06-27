---
name: docker-access
description: Verify Docker availability and run containers on this host.
---

# Docker Access

## When to Use
Verify Docker availability and run containers on this host.

## Overview
This skill contains a reusable operational workflow. Follow the existing task-specific steps and examples in the sections below.

## Pitfalls
- Do not hardcode credentials, tokens, or personal secrets.
- Verify external service URLs, paths, and permissions before making changes.
- Keep generated outputs reproducible and record input assumptions.

## Verification
- Confirm required inputs and credentials are available.
- Run the smallest safe command or example before scaling up.
- Check produced files, API responses, or plots before reporting success.


## Environment
- **Docker:** v29.2.1
- **Daemon:** Running (local)
- **User:** Can pull and run arbitrary containers

## Quick Checks

```bash
docker version              # verify daemon
docker run --rm hello-world # quick smoke test
```

## Digital Twin Docker Compose

```bash
docker compose -f docker-compose.yml -f docker-compose-hifis.yml up -d
```

Access: Web UI at `localhost:5000`

## Known Issues
- MongoDB must have accelerator lattice data pre-loaded
- Crash signature: `TypeError: Accelerator.__init__() missing 1 required keyword-only argument: 'energy'`
