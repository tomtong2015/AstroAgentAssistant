# Venv Provisioning Notes for J-UBIK Skill

## prerequisites.python: frontmatter, NOT code blocks

The Hermes venv provisioning system (`_extract_python_requirements` in `tools/skills_hub.py`) parses SKILL.md frontmatter via `_parse_frontmatter_dict`. It reads the `prerequisites.python` list from the YAML frontmatter between the opening and closing `---` delimiters.

**It does NOT look inside code blocks.** Placing prerequisites inside ````yaml` ... ```` in the body will silently result in zero requirements — the venv will never be provisioned, with no error surfaced to the agent (provisioning is "non-fatal").

Correct:
```yaml
---
name: my-skill
prerequisites:
  python:
    - "package>=1.0"
---
```

Incorrect (silent failure):
```markdown
## Prerequisites

```yaml
prerequisites:
  python:
    - "package>=1.0"
```
```

## `uv` not on PATH

In this environment, `uv` lives at `/opt/conda/bin/uv`, which is NOT on the default PATH. The provisioning system's `_find_uv()` uses `shutil.which("uv")` which may return `None`, falling back to `python3 -m venv` + `pip install`. The fallback works but is slower.

If provisioning fails silently, check:
1. Is `prerequisites` in the actual frontmatter (not a code block)?
2. Run `which uv` manually to verify availability.
3. Check logs: `~/.hermes/logs/` — provisioning errors are logged as warnings.

## "Non-fatal" provisioning means "invisible"

`_sync_skill_venv` wraps provisioning in a bare `try/except Exception` and returns a note string, NOT a raised error. The `skill_manage` tool result still shows `success: true` even when provisioning fails. Always verify the venv exists after creating/editing a skill with prerequisites.
