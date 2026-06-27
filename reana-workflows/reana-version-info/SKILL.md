---
name: reana-version-info
category: devops
description: Quick reference for REANA client and server versions for dev and production backends used by the user.
---
# REANA Version Information

## When to Use
Quick reference for REANA client and server versions for dev and production backends used by the user.

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


## Development backend (`https://reana-dev.kube.aip.de`)
- **REANA server version**: `0.95.0a4`
- **REANA client version** (Docker image `reanahub/reana-client:0.95.0-alpha.3`): `0.95.0a3`

## Production backend (`https://reana-p4n.aip.de`)
- **REANA server version**: `0.9.4`
- **REANA client version** (Docker image `reanahub/reana-client:0.95.0-alpha.3`): `0.95.0a3`

> Note: The client version is the same for both environments; only the server versions differ.

## Usage
When you need to reference the current REANA versions, consult this skill. It can be loaded with:
```
skill_view('reana-version-info')
```

Keep this skill up‑to‑date if the REANA versions change.
