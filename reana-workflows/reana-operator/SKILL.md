---
name: reana-operator
description: >-
  Use when operating REANA from natural language: check job status, list available backends,
  show recent jobs by status, scaffold reana.yaml projects, run code as REANA workflows,
  inspect logs, validate YAML, and download outputs using REANA_SERVER_URL and
  REANA_ACCESS_TOKEN from the environment.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [reana, workflow, operator, jobs, status, reproducibility]
    category: reana-workflows
    related_skills: [reana-client-config, reana-client-docker, reana-serial-python, reana-workflow-best-practices, reana-run-script-with-workspace]
---

# REANA Operator

## Overview

This is the front-door skill for day-to-day REANA operations. Use it to translate user requests into safe, concrete REANA actions: check workflow status, list recent jobs, inspect failed logs, show the active backend, scaffold a new project, generate `reana.yaml`, submit a workflow, validate inputs, and download outputs.

The implementation assumes credentials are already present in the shell environment:

```bash
export REANA_SERVER_URL="https://..."
export REANA_ACCESS_TOKEN="..."
```

Do not ask the user to paste tokens into files. Do not write tokens into `reana.yaml`, logs, README files, or commits.

## When to Use

Use this skill when the user asks any of the following:

- “What is the status of my REANA job?”
- “Show recent REANA jobs.”
- “List failed / running / pending / successful workflows.”
- “Which REANA backend am I using?”
- “Can REANA connect?”
- “Run this Python code on REANA.”
- “Create a REANA job for this project.”
- “Generate an appropriate `reana.yaml`.”
- “Show logs for the failed job.”
- “Download outputs from workflow X.”

Do not use this skill for generic local-only scripts that do not need REANA.

## Helper CLI

This skill ships a helper:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py --help
```

It prefers a native `reana-client` if installed. Otherwise it uses Docker with:

```bash
REANA_CLIENT_IMAGE=${REANA_CLIENT_IMAGE:-reanahub/reana-client:0.95.0-alpha.3}
```

The helper never prints `REANA_ACCESS_TOKEN`.

## Quick Commands

### Check backend/credentials

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py backends
python reana-workflows/reana-operator/scripts/reana_operator.py ping
```

### Recent jobs

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py recent --limit 10
python reana-workflows/reana-operator/scripts/reana_operator.py recent --status failed --limit 10
python reana-workflows/reana-operator/scripts/reana_operator.py recent --status running --limit 10
python reana-workflows/reana-operator/scripts/reana_operator.py recent --status success --limit 10
python reana-workflows/reana-operator/scripts/reana_operator.py recent --status pending --limit 10
```

Status aliases are normalized:

| User wording | REANA statuses checked |
|---|---|
| success, successful, finished | `finished`, `succeeded`, `success` |
| failed, error | `failed`, `failure`, `error` |
| pending, queued | `created`, `queued`, `pending` |
| running, active | `running`, `active` |
| stopped, cancelled | `stopped`, `cancelled`, `canceled`, `deleted` |

### Job status and logs

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py status <workflow-name-or-id>
python reana-workflows/reana-operator/scripts/reana_operator.py logs <workflow-name-or-id> --tail 100
```

If a workflow failed, fetch logs immediately and summarize the likely failure class: missing input, YAML validation, missing package, environment mismatch, timeout, memory, or remote-data access.

### Download outputs

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py download <workflow-name-or-id> --out outputs/<workflow>
```

## Creating a REANA Job from Code

For a quick Python job:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py scaffold   --project /tmp/reana-demo   --script analysis.py   --code 'print("hello REANA"); open("output.txt", "w").write("hello\n")'   --output output.txt

python reana-workflows/reana-operator/scripts/reana_operator.py validate --project /tmp/reana-demo
python reana-workflows/reana-operator/scripts/reana_operator.py run --project /tmp/reana-demo --workflow reana-demo --timestamp
```

For an existing project:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py scaffold   --project ./my-analysis   --script analysis.py   --output result.png   --output summary.csv
```

The scaffold creates:

```text
my-analysis/
  reana.yaml
  .reanaignore
  analysis.py          # only if --code was passed or a missing script should be stubbed
  requirements.txt     # optional, used if present
```

## `reana.yaml` Defaults

The generated workflow uses the AIP-compatible serial pattern:

```yaml
version: 0.9.0
inputs:
  files:
    - analysis.py
    - requirements.txt
workflow:
  type: serial
  specification:
    steps:
      - name: my-analysis
        environment: gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c
        kubernetes_memory_limit: "32Gi"
        kubernetes_job_timeout: 7200
        commands:
          - bash -lc 'cd "$REANA_WORKSPACE" && if [ -f requirements.txt ]; then pip install --quiet -r requirements.txt; fi && python3 analysis.py'
        outputs:
          files:
            - output.txt
outputs:
  files:
    - output.txt
```

Adjust the environment with `--environment` only when a known approved image is required.

## Project-Type Handling

Supported now:

| Input | Behavior |
|---|---|
| `--script analysis.py` | run `python3 analysis.py`; install `requirements.txt` if present |
| `--script run.sh` | run `bash run.sh` |
| `--command '...'` | run the explicit shell command |
| `--code '...'` | write code into the script, scaffold, validate, then run |

Planned/advanced cases to handle manually for now:

| Project type | Recommended handling |
|---|---|
| notebook `.ipynb` | convert to a Python script or use a verified Jupyter-capable REANA image |
| `Snakefile` | use only after confirming a Snakemake-capable environment |
| `Makefile` | use `--command 'make <target>'` and declare outputs explicitly |
| large input data | stage only small scripts/config; fetch remote data inside the workflow |

## Validation Checklist

Before running, the helper checks:

- `reana.yaml` exists and parses as YAML
- all `inputs.files` exist locally
- no token/access-token text appears in `reana.yaml`
- outputs are declared
- memory is set to a 32 GiB/GB default
- no inline heredoc script block is present

Run explicitly:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py validate --project ./my-analysis
```

## Workspace Hygiene

`reana-client run` may upload local project content. Keep projects small and explicit.

The scaffold writes `.reanaignore` with common exclusions:

```text
.git/
.env
.reana/
__pycache__/
*.pem
*.key
*token*
*secret*
*password*
```

Before submitting, inspect the project tree and remove large or private files.

## Operational Recipes

### “What backend am I using?”

1. Run `backends`.
2. Report `REANA_SERVER_URL`, whether the token is set, client mode, and any local config profiles.
3. If credentials are set, run `ping` and report server/client versions.

### “Show recent failed jobs”

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py recent --status failed --limit 10
```

If exactly one recent failed job is relevant, follow with:

```bash
python reana-workflows/reana-operator/scripts/reana_operator.py logs <workflow> --tail 120
```

### “Run this code on REANA”

1. Create a clean project directory.
2. Write the code to `analysis.py`.
3. Scaffold `reana.yaml` with declared outputs.
4. Validate.
5. Submit with `run --timestamp`.
6. Return status/log/download commands.

### “Create a REANA project for this repository”

1. Detect the main script or ask only if ambiguous.
2. Add/keep `requirements.txt` if present.
3. Generate `reana.yaml` with the script as an input file.
4. Validate all input files.
5. Do not submit until the user confirms if project upload size or output names are unclear.

## Common Pitfalls

1. **Credentials in files** — never write `REANA_ACCESS_TOKEN` or access tokens into `reana.yaml`, `.reana/config.yaml` in a public repo, README, or logs.
2. **Wrong working directory** — always run scripts from `$REANA_WORKSPACE` inside REANA.
3. **Missing input file** — any script referenced by the command must be declared under `inputs.files` and exist locally.
4. **Inline YAML scripts** — avoid heredocs inside `reana.yaml`; use separate `analysis.py` or `run.sh` files.
5. **Huge uploads** — do not submit a full repository with large data, `.git/`, caches, or credentials. Use remote data access inside the workflow.
6. **Output not declared** — REANA will not expose artifacts reliably unless outputs are listed.
7. **Ambiguous workflow names** — use `--timestamp` for new submissions to avoid collisions.
8. **Unverified environment images** — only change `--environment` to a known REANA image.

## Verification

- `python scripts/reana_operator.py --help` works.
- `scaffold` creates `reana.yaml` and `.reanaignore`.
- `validate` passes on the generated scaffold.
- `backends` reports unset/set credentials without exposing token values.
- With real environment variables set, `ping` connects to REANA.
- After `run`, `status`, `logs`, and `download` commands operate on the submitted workflow.
