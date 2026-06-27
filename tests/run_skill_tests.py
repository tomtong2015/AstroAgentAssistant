#!/usr/bin/env python3
"""Safe repository-wide skill audit and report generator.

This script performs static, non-destructive tests for every SKILL.md file and
supporting Python/YAML/JSON file in the repository. It intentionally avoids
printing secret values: secret-like detections are summarized as counts and
sanitized pattern labels only.
"""
from __future__ import annotations

import ast
import csv
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
EXCLUDE_DIRS = {".git", "tests", "__pycache__"}
REQUIRED_SECTIONS = ["When to Use", "Procedure", "Pitfalls", "Verification"]
SECRET_PATTERNS = {
    "github_token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    "reana_token_assignment": re.compile(r"REANA_ACCESS_TOKEN\s*[:=]\s*['\"]?[^\s'\"<${]+"),
    "generic_secret_assignment": re.compile(r"(?i)\b(password|passwd|access_token|api[_-]?key|secret)\s*[:=]\s*['\"]?([^\s'\"<${][^\s'\"]{4,})"),
}
PLACEHOLDER_HINTS = ("placeholder", "example", "your-", "xxxx", "xxx", "token", "<", "${", "{", "REDACTED", "not-needed")


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def iter_files(pattern: str):
    for p in sorted(REPO.rglob(pattern)):
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        yield p


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str | None, str]:
    if not text.startswith("---"):
        return {}, "missing opening frontmatter marker", text
    m = re.search(r"\n---\s*\n", text[3:])
    if not m:
        return {}, "missing closing frontmatter marker", text
    end = 3 + m.start()
    raw = text[3:end]
    body = text[3 + m.end():]
    try:
        data = yaml.safe_load(raw)
    except Exception as exc:
        return {}, f"frontmatter YAML parse error: {type(exc).__name__}", body
    if not isinstance(data, dict):
        return {}, "frontmatter is not a mapping", body
    return data, None, body


def skill_tests(path: Path) -> dict[str, Any]:
    text = path.read_text(errors="replace")
    fm, fm_error, body = parse_frontmatter(text)
    name = str(fm.get("name") or path.parent.name)
    desc = str(fm.get("description") or "")
    section_hits = {sec: bool(re.search(rf"^##\s+{re.escape(sec)}\b", text, re.M | re.I)) for sec in REQUIRED_SECTIONS}
    related = []
    meta = fm.get("metadata") or {}
    if isinstance(meta, dict):
        hermes = meta.get("hermes") or {}
        if isinstance(hermes, dict):
            related = hermes.get("related_skills") or []
    if not related and fm.get("related_skills"):
        related = fm.get("related_skills")
    checks = {
        "frontmatter": fm_error is None,
        "name_present": bool(fm.get("name")),
        "description_present": bool(desc),
        "description_length": 0 < len(desc) <= 1024,
        "body_present": bool(body.strip()),
        "required_sections": all(section_hits.values()),
        "author_present": bool(fm.get("author")),
        "license_present": bool(fm.get("license")),
        "canonical_routing": ("## Canonical Routing" in text),
    }
    status = "PASS" if all(checks[k] for k in ["frontmatter", "name_present", "description_present", "description_length", "body_present", "required_sections"]) else "WARN"
    quality_issue_keys = {"author_present", "license_present", "canonical_routing"}
    issues = []
    if fm_error:
        issues.append(fm_error)
    for key, ok in checks.items():
        if not ok and key not in quality_issue_keys:
            issues.append(key)
    quality_notes = [key for key, ok in checks.items() if (not ok and key in quality_issue_keys)]
    return {
        "path": rel(path),
        "category": path.relative_to(REPO).parts[0],
        "name": name,
        "description": " ".join(desc.split()),
        "author": str(fm.get("author") or ""),
        "license": str(fm.get("license") or ""),
        "related_count": len(related) if isinstance(related, list) else 0,
        "checks": checks,
        "section_hits": section_hits,
        "status": status,
        "issues": issues,
        "quality_notes": quality_notes,
        "size_bytes": path.stat().st_size,
        "sha256_12": hashlib.sha256(text.encode(errors="replace")).hexdigest()[:12],
    }


def test_python_file(path: Path) -> dict[str, Any]:
    text = path.read_text(errors="replace")
    try:
        ast.parse(text)
        syntax_ok = True
        error = ""
    except SyntaxError as exc:
        syntax_ok = False
        error = f"SyntaxError line {exc.lineno}: {exc.msg}"
    return {"path": rel(path), "kind": "python", "status": "PASS" if syntax_ok else "FAIL", "error": error}


def test_yaml_json_file(path: Path) -> dict[str, Any]:
    text = path.read_text(errors="replace")
    kind = path.suffix.lower().lstrip(".")
    try:
        if kind in {"yaml", "yml"}:
            yaml.safe_load(text)
        elif kind == "json":
            json.loads(text)
        return {"path": rel(path), "kind": kind, "status": "PASS", "error": ""}
    except Exception as exc:
        return {"path": rel(path), "kind": kind, "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}


def secret_scan_file(path: Path) -> list[dict[str, Any]]:
    hits = []
    text = path.read_text(errors="replace")
    for idx, line in enumerate(text.splitlines(), start=1):
        for label, pattern in SECRET_PATTERNS.items():
            for m in pattern.finditer(line):
                token = m.group(0)
                low = token.lower()
                placeholder = any(h.lower() in low for h in PLACEHOLDER_HINTS)
                hits.append({
                    "path": rel(path),
                    "line": idx,
                    "pattern": label,
                    "placeholder_like": placeholder,
                    "fingerprint": hashlib.sha256(token.encode()).hexdigest()[:12],
                })
    return hits


def run_root_audit() -> dict[str, Any]:
    audit_script = Path("/tmp/audit_astroagent.py")
    if not audit_script.exists():
        return {"status": "SKIP", "reason": "audit script not found"}
    cp = subprocess.run([sys.executable, str(audit_script)], cwd=REPO, text=True, capture_output=True, timeout=120)
    if cp.returncode != 0:
        return {"status": "FAIL", "stdout_tail": cp.stdout[-1000:], "stderr_tail": cp.stderr[-1000:]}
    try:
        data = json.loads(cp.stdout)
    except json.JSONDecodeError:
        return {"status": "FAIL", "reason": "audit script did not produce JSON"}
    ok = (
        not data.get("readme_count_mismatches")
        and not data.get("frontmatter_or_required_field_errors")
        and not data.get("duplicate_skill_names")
        and not data.get("missing_sections_counts")
    )
    return {"status": "PASS" if ok else "FAIL", "data": data}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


def make_diagram(skill_rows: list[dict[str, Any]], support_rows: list[dict[str, Any]], out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    cats = sorted({r["category"] for r in skill_rows})
    pass_counts = []
    warn_counts = []
    fail_counts = []
    for cat in cats:
        rows = [r for r in skill_rows if r["category"] == cat]
        pass_counts.append(sum(r["status"] == "PASS" for r in rows))
        warn_counts.append(sum(r["status"] == "WARN" for r in rows))
        fail_counts.append(sum(r["status"] == "FAIL" for r in rows))
    y = np.arange(len(cats))
    fig_h = max(7, 0.42 * len(cats) + 2)
    fig, ax = plt.subplots(figsize=(12, fig_h), facecolor="white")
    ax.barh(y, pass_counts, color="#2ca25f", label="PASS")
    ax.barh(y, warn_counts, left=pass_counts, color="#feb24c", label="WARN")
    left = [a + b for a, b in zip(pass_counts, warn_counts)]
    ax.barh(y, fail_counts, left=left, color="#de2d26", label="FAIL")
    ax.set_yticks(y, cats)
    ax.invert_yaxis()
    ax.set_xlabel("Number of skills")
    ax.set_title("AstroAgentAssistant per-skill static test result summary")
    ax.legend(loc="lower right")
    for i, total in enumerate([a + b + c for a, b, c in zip(pass_counts, warn_counts, fail_counts)]):
        ax.text(total + 0.1, i, str(total), va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)


def make_pdf(summary: dict[str, Any], skill_rows: list[dict[str, Any]], support_rows: list[dict[str, Any]], secret_summary: dict[str, Any], diagram: Path, out: Path) -> None:
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import textwrap

    with PdfPages(out) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        ax = fig.add_subplot(111)
        ax.axis("off")
        lines = [
            "AstroAgentAssistant Skill Test Report",
            "",
            f"Generated UTC: {summary['generated_utc']}",
            f"Git commit: {summary.get('git_commit', 'unknown')}",
            "",
            f"Skills tested: {summary['skills_total']}",
            f"Skill PASS/WARN/FAIL: {summary['skills_pass']} / {summary['skills_warn']} / {summary['skills_fail']}",
            f"Support files tested: {summary['support_total']}",
            f"Support PASS/FAIL: {summary['support_pass']} / {summary['support_fail']}",
            f"Secret scan serious hits: {secret_summary['serious_hits']}",
            f"Secret scan placeholder-like hits: {secret_summary['placeholder_like_hits']}",
            "",
            "Scope:",
            "Static, non-destructive tests for every SKILL.md and support Python/YAML/JSON file. The report does not include secret values; secret-like detections are reported only as sanitized counts/pattern labels in JSON.",
            "",
            "Interpretation:",
            "PASS means structural checks passed. WARN means the skill is usable but missing one or more quality metadata/section checks. FAIL means a parse/syntax check failed and needs attention.",
        ]
        y = 0.97
        for line in lines:
            ax.text(0.05, y, line, fontsize=12 if line.endswith("Report") else 9, weight="bold" if line.endswith("Report") else "normal", va="top")
            y -= 0.035 if line else 0.02
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        img = plt.imread(diagram)
        fig, ax = plt.subplots(figsize=(11.69, 8.27), facecolor="white")
        ax.imshow(img)
        ax.axis("off")
        ax.set_title("Per-category skill test result diagram", fontsize=14)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        warnings = [r for r in skill_rows if r["status"] != "PASS"]
        for page_start in range(0, len(warnings), 22):
            fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
            ax = fig.add_subplot(111)
            ax.axis("off")
            ax.text(0.05, 0.97, "Skill WARN/FAIL details", fontsize=14, weight="bold", va="top")
            y = 0.92
            for r in warnings[page_start:page_start+22]:
                issue_text = ", ".join(r["issues"][:6])
                wrapped = textwrap.wrap(f"{r['status']} {r['name']} ({r['path']}): {issue_text}", width=110)
                for wline in wrapped[:3]:
                    ax.text(0.05, y, wline, fontsize=7.5, va="top")
                    y -= 0.024
                y -= 0.008
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)


def main() -> int:
    TESTS.mkdir(exist_ok=True)
    skill_rows = [skill_tests(p) for p in iter_files("SKILL.md")]
    names = [r["name"] for r in skill_rows]
    duplicates = {name for name, count in Counter(names).items() if count > 1}
    for r in skill_rows:
        if r["name"] in duplicates:
            r["status"] = "FAIL"
            r["issues"].append("duplicate_name")
            r["checks"]["duplicate_name"] = False
        else:
            r["checks"]["duplicate_name"] = True

    support_rows = []
    for p in iter_files("*.py"):
        support_rows.append(test_python_file(p))
    for pattern in ("*.yaml", "*.yml", "*.json"):
        for p in iter_files(pattern):
            support_rows.append(test_yaml_json_file(p))

    secret_hits = []
    for pattern in ("*.md", "*.py", "*.yaml", "*.yml", "*.json"):
        for p in iter_files(pattern):
            secret_hits.extend(secret_scan_file(p))
    serious_hits = [h for h in secret_hits if not h["placeholder_like"]]
    secret_summary = {
        "total_hits": len(secret_hits),
        "serious_hits": len(serious_hits),
        "placeholder_like_hits": len(secret_hits) - len(serious_hits),
        "patterns": dict(Counter(h["pattern"] for h in secret_hits)),
        "serious_patterns": dict(Counter(h["pattern"] for h in serious_hits)),
        "sanitized_hits": secret_hits,
    }

    root_audit = run_root_audit()
    git_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, text=True, capture_output=True).stdout.strip()
    summary = {
        "generated_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "git_commit": git_commit,
        "skills_total": len(skill_rows),
        "skills_pass": sum(r["status"] == "PASS" for r in skill_rows),
        "skills_warn": sum(r["status"] == "WARN" for r in skill_rows),
        "skills_fail": sum(r["status"] == "FAIL" for r in skill_rows),
        "support_total": len(support_rows),
        "support_pass": sum(r["status"] == "PASS" for r in support_rows),
        "support_fail": sum(r["status"] == "FAIL" for r in support_rows),
        "secret_serious_hits": secret_summary["serious_hits"],
        "root_audit_status": root_audit["status"],
        "categories": dict(Counter(r["category"] for r in skill_rows)),
    }

    (TESTS / "skill_test_results.json").write_text(json.dumps({"summary": summary, "skills": skill_rows, "support_files": support_rows, "root_audit": root_audit, "secret_scan": secret_summary}, indent=2) + "\n")
    write_csv(TESTS / "skill_test_results.csv", skill_rows, ["path", "category", "name", "status", "issues", "quality_notes", "author", "license", "related_count", "size_bytes", "sha256_12"])
    write_csv(TESTS / "support_file_test_results.csv", support_rows, ["path", "kind", "status", "error"])
    (TESTS / "secret_scan_summary.json").write_text(json.dumps(secret_summary, indent=2) + "\n")

    diagram = TESTS / "skill_test_result_diagram.png"
    make_diagram(skill_rows, support_rows, diagram)

    md = [
        "# AstroAgentAssistant Skill Test Report",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Git commit: `{summary['git_commit']}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Skills tested | {summary['skills_total']} |",
        f"| Skill PASS | {summary['skills_pass']} |",
        f"| Skill WARN | {summary['skills_warn']} |",
        f"| Skill FAIL | {summary['skills_fail']} |",
        f"| Support files tested | {summary['support_total']} |",
        f"| Support PASS | {summary['support_pass']} |",
        f"| Support FAIL | {summary['support_fail']} |",
        f"| Serious secret hits | {summary['secret_serious_hits']} |",
        f"| Root audit | {summary['root_audit_status']} |",
        "",
        "![Per-skill test result diagram](skill_test_result_diagram.png)",
        "",
        "## Per-skill Results",
        "",
        "| Skill | Category | Status | Issues | Quality notes |",
        "|---|---|---:|---|---|",
    ]
    for r in skill_rows:
        md.append(f"| `{r['name']}` | `{r['category']}` | {r['status']} | {', '.join(r['issues']) or '-'} | {', '.join(r.get('quality_notes', [])) or '-'} |")
    md += ["", "## Support File Results", "", "| File | Kind | Status | Error |", "|---|---|---:|---|"]
    for r in support_rows:
        md.append(f"| `{r['path']}` | {r['kind']} | {r['status']} | {r['error'] or '-'} |")
    md += ["", "## Secret Scan", "", "The report stores no secret values. Secret-like findings are summarized by pattern labels and fingerprints only.", "", f"Serious hits: **{secret_summary['serious_hits']}**", f"Placeholder-like hits: **{secret_summary['placeholder_like_hits']}**", ""]
    (TESTS / "skill_test_report.md").write_text("\n".join(md))

    try:
        make_pdf(summary, skill_rows, support_rows, secret_summary, diagram, TESTS / "skill_test_report.pdf")
        pdf_status = "PASS"
    except Exception as exc:
        pdf_status = f"FAIL: {type(exc).__name__}: {exc}"
        (TESTS / "pdf_generation_error.txt").write_text(pdf_status + "\n")

    print(json.dumps({"summary": summary, "pdf_generation": pdf_status, "outputs": sorted(p.name for p in TESTS.iterdir())}, indent=2))
    return 0 if summary["skills_fail"] == 0 and summary["support_fail"] == 0 and summary["secret_serious_hits"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
