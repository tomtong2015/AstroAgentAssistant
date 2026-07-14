---
name: reana-aip
description: Author, validate, and run REANA workflows under AIP conventions — canonical reana.yaml template, the approved environment images, mandatory reana-client validate, submit/monitor recipe, GitLab + DRP-card hand-off.
version: 2.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [reana, workflow, reana.yaml, reproducibility, astronomy, validation]
    category: workflows
    related_skills: [reana-serial-python, drphub-cards, docs-mcp-at-aip]
---

# REANA AIP Workflow

## When to Use
Use this skill when creating, validating, or running a REANA workflow at AIP —
including workflows that will back a DRP-Hub card ("Run on REANA"). For the
full Python-analysis file layout (script + Parquet cache + plots), also load
**reana-serial-python**. For REANA spec questions beyond this page, query the
AIP docs MCP server (**docs-mcp-at-aip**) if its tools are available — it
indexes the REANA docs and the environments guide; otherwise use the baked
reference below.

## The canonical reana.yaml (serial — validated shape)
```yaml
version: 0.9.0
inputs:
  files:
    - script.py            # EVERY file the steps need must be listed here
workflow:
  type: serial
  specification:
    steps:
      - name: analysis
        environment: 'gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro.9845'
        kubernetes_memory_limit: '8Gi'
        commands:
          - python3 script.py
outputs:
  files:
    - output.png
```
Structure rules (getting these wrong is the #1 failure mode):
- `inputs.files:` / `outputs.files:` are LISTS OF PATHS — never name/path pairs.
- The `workflow:` block with `type` + `specification.steps` is REQUIRED —
  there is no top-level `command:` or `environment:` in the REANA spec.
- `environment:` lives PER STEP; plain image ref, **no `docker://` prefix**,
  and gitlab-p4n images need the **`:5005` registry port**.
- Memory: set `kubernetes_memory_limit` explicitly per step — `'8Gi'` for
  small demos, up to `'32Gi'` for heavy analysis (AIP convention).

## Approved environments (do NOT invent images)
| Image ref | Use for |
|---|---|
| `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro.9845` | basic astro/scientific python (scipy, numpy, pandas, matplotlib, astropy, seaborn) |
| `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c` | + ML/dask/s3fs/datashader/holoviews/pyvo stack |
| `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py312-ml-vsc.23d98846` | py3.12 interactive stack (JupyterLab/VSCode; incl. fastparquet) |

Authoritative, current list (refresh from here when in doubt — tags rotate):
```bash
curl -s "https://gitlab-p4n.aip.de/punch_public/reana/environments/-/raw/main/README.md" | grep -B1 -A1 "Image path"
```

## MANDATORY: validate before anything else
```bash
reana-client validate -f reana.yaml
```
Run this after writing/altering reana.yaml and BEFORE `create`/`run`/making a
DRP card. All three checks must say SUCCESS. Validation checks the schema,
not image existence — the environment ref must still come from the table above.

## Auth
In DRP-Hub `drphub_service` sessions, reana-client is preconfigured (token
recovered automatically). Check with `reana-client ping` — if it fails, ask
the user for their REANA token (DRP-Hub profile page) rather than guessing.

## Submit & monitor
```bash
cd <workflow-dir>                       # contains reana.yaml + inputs
reana-client create -w myproj           # or: reana-client run -w myproj (create+upload+start)
reana-client upload -w myproj
reana-client start -w myproj
reana-client status -w myproj           # poll until finished/failed
reana-client logs -w myproj | tail -50  # on failure: read the step logs
reana-client download output.png -w myproj
```
NB on AIP pods, `reana-client` write operations trigger a human approval card
in the chat UI — tell the user to approve it; this is expected, not an error.

## Publishing to GitLab (for a DRP card)
The pod's baked token (`AIP_MAINT_GITLAB_TOKEN`) is a **project bot of
`p4nreana/reana-env`** — it cannot create projects, cannot be added to other
projects, and can only push to reana-env. Publishing a USER repo therefore
needs the user's help twice (both are one-click; verified flow):
1. **User creates the project**: `https://gitlab-p4n.aip.de/projects/new`,
   visibility **public or internal** (DRP-Hub must be able to clone it).
2. **User creates a project access token on it** and pastes it to you:
   project → Settings → Access Tokens → name e.g. `ori-push`, role
   **Maintainer** (Developer cannot push the protected default branch),
   scope `write_repository`, a short expiry.
3. Push the workflow dir (reana.yaml at the REPO ROOT + all input files,
   NOT the generated outputs — .gitignore them):
```bash
git init -b main && git add -A && git commit -m "REANA workflow"
git push https://<token-name>:<token>@gitlab-p4n.aip.de/<namespace>/<project>.git main
```
   Offer to store the token for reuse:
   `reana-client secrets-add --env GITLAB_PUSH_TOKEN=<token>` (lands in the
   env after the next session re-create).
4. Then create the card with **drphub-cards** — see its "runnable card
   pre-flight"; the card's `workflow_file`/`env_image`/`entry_command` must
   MATCH the repo's reana.yaml, and pin `git_commit` to the pushed SHA.

## Pitfalls
- Inventing environment images (or dropping the `:5005` port, or adding a
  `docker://` prefix) → ImagePullBackOff or validation confusion.
- Forgetting a script in `inputs.files` → step fails with file-not-found.
- Skipping `reana-client validate` → broken card runs for every future user.
- Don't ask users to install/configure reana-client in drphub sessions — it
  already works.
