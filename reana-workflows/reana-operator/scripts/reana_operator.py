#!/usr/bin/env python3
"""REANA operator helper.

Small, token-safe CLI for common day-to-day REANA operations. It assumes
REANA_SERVER_URL and REANA_ACCESS_TOKEN are set for commands that contact REANA.
It never prints the access token.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

DEFAULT_IMAGE = "reanahub/reana-client:0.95.0-alpha.3"
DEFAULT_ENVIRONMENT = "gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c"
VALID_CLIENT_MODES = {"auto", "native", "docker"}
STATUS_ALIASES = {
    "success": {"finished", "succeeded", "success"},
    "successful": {"finished", "succeeded", "success"},
    "finished": {"finished", "succeeded", "success"},
    "failed": {"failed", "failure", "error"},
    "error": {"failed", "failure", "error"},
    "pending": {"created", "queued", "pending"},
    "queued": {"created", "queued", "pending"},
    "running": {"running", "active"},
    "active": {"running", "active"},
    "stopped": {"stopped", "cancelled", "canceled", "deleted"},
    "cancelled": {"stopped", "cancelled", "canceled", "deleted"},
}


def fail(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def require_reana_env() -> None:
    missing = [k for k in ("REANA_SERVER_URL", "REANA_ACCESS_TOKEN") if not os.environ.get(k)]
    if missing:
        fail("Set required environment variables first: " + ", ".join(missing))


def client_image() -> str:
    return os.environ.get("REANA_CLIENT_IMAGE", DEFAULT_IMAGE)


def client_mode() -> str:
    mode = os.environ.get("REANA_CLIENT_MODE", "auto").strip().lower() or "auto"
    if mode not in VALID_CLIENT_MODES:
        fail(f"Invalid REANA_CLIENT_MODE={mode!r}; expected one of: {', '.join(sorted(VALID_CLIENT_MODES))}")
    return mode


def native_client() -> str | None:
    return shutil.which("reana-client")


def docker_client() -> str | None:
    return shutil.which("docker")


def check_docker_daemon(docker: str) -> tuple[bool, str]:
    cp = subprocess.run([docker, "version", "--format", "{{.Server.Version}}"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cp.returncode == 0:
        return True, cp.stdout.strip() or "available"
    return False, (cp.stderr or cp.stdout).strip()


def selected_client() -> str:
    mode = client_mode()
    native = native_client()
    docker = docker_client()
    if mode == "native":
        if not native:
            fail("REANA_CLIENT_MODE=native but reana-client was not found on PATH")
        return "native"
    if mode == "docker":
        if docker is None:
            fail("REANA_CLIENT_MODE=docker but docker was not found on PATH")
        ok, msg = check_docker_daemon(docker)
        if not ok:
            fail("Docker is installed but the daemon is not reachable: " + msg)
        return "docker"
    if native:
        return "native"
    if docker is not None:
        ok, msg = check_docker_daemon(docker)
        if not ok:
            fail("reana-client is missing and Docker daemon is not reachable: " + msg)
        return "docker"
    fail("Neither native reana-client nor Docker is available. Install reana-client or Docker.")
    raise AssertionError("unreachable")


def reana_command(args: list[str], mount: Path | None = None) -> list[str]:
    """Return a native or Dockerized reana-client command."""
    backend = selected_client()
    if backend == "native":
        native = native_client()
        if native is not None:
            return [native, *args]
        fail("reana-client disappeared from PATH")
    docker = docker_client()
    if not docker:
        fail("docker disappeared from PATH")
    cmd = [
        docker,
        "run",
        "--rm",
        "-e",
        "REANA_SERVER_URL",
        "-e",
        "REANA_ACCESS_TOKEN",
    ]
    if mount:
        mount = mount.resolve()
        cmd += ["-v", f"{mount}:/workspace", "-w", "/workspace"]
    cmd += [client_image(), *args]
    return cmd


def run_reana(args: list[str], *, mount: Path | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    require_reana_env()
    cmd = reana_command(args, mount=mount)
    # Native reana-client needs to run from the project directory so that
    # reana.yaml and input files are uploaded from the intended workspace.
    # Dockerized mode uses -v <project>:/workspace -w /workspace instead.
    cwd = mount.resolve() if mount and selected_client() == "native" else None
    if capture:
        return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    printable = " ".join(shlex.quote(x) for x in cmd)
    if cwd:
        print(f"$ (cd {shlex.quote(str(cwd))} && {printable})")
    else:
        print(f"$ {printable}")
    return subprocess.run(cmd, text=True, cwd=cwd)


def load_json_list() -> list[dict[str, Any]]:
    cp = run_reana(["list", "-v", "--json"], capture=True)
    if cp.returncode != 0:
        print(cp.stderr.strip(), file=sys.stderr)
        fail("reana-client list failed", cp.returncode)
    try:
        data = json.loads(cp.stdout or "[]")
    except json.JSONDecodeError as exc:
        print(cp.stdout, file=sys.stderr)
        fail(f"Could not parse reana-client JSON output: {exc}")
    if not isinstance(data, list):
        fail("Expected JSON list from reana-client list -v --json")
    return data


def normalize_status_filter(value: str | None) -> set[str] | None:
    if not value:
        return None
    key = value.strip().lower()
    return STATUS_ALIASES.get(key, {key})


def row_value(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return str(value)
    return "-"


def print_table(rows: list[list[str]], headers: list[str]) -> None:
    if not rows:
        print("No matching workflows found.")
        return
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for row in rows:
        print(fmt.format(*row))


def cmd_ping(_: argparse.Namespace) -> int:
    cp = run_reana(["ping"])
    return cp.returncode


def cmd_backends(_: argparse.Namespace) -> int:
    print("Active REANA environment:")
    print(f"  REANA_SERVER_URL: {os.environ.get('REANA_SERVER_URL', '<unset>')}")
    print(f"  Token configured: {'yes' if os.environ.get('REANA_ACCESS_TOKEN') else 'no'}")
    print(f"  REANA_CLIENT_MODE: {client_mode()}")
    print(f"  selected client: {selected_client()}")
    print(f"  REANA_CLIENT_IMAGE: {client_image()}")
    print(f"  native reana-client: {native_client() or '<not found>'}")
    docker = docker_client()
    print(f"  docker: {docker or '<not found>'}")
    if docker:
        ok, msg = check_docker_daemon(docker)
        print(f"  docker daemon: {'available' if ok else 'unavailable'}{(': ' + msg) if msg else ''}")
    print("\nKnown profiles from config files:")
    found = False
    try:
        import yaml  # type: ignore
    except Exception:
        yaml = None
    for cfg in [Path.home() / ".reana" / "config.yaml", Path(".reana") / "config.yaml"]:
        if not cfg.exists():
            continue
        found = True
        print(f"  {cfg}:")
        if not yaml:
            print("    PyYAML unavailable; cannot parse")
            continue
        data = yaml.safe_load(cfg.read_text()) or {}
        if isinstance(data, dict):
            for name, profile in data.items():
                if isinstance(profile, dict):
                    print(f"    {name}: {profile.get('server_url', '<no server_url>')}")
    if not found:
        print("  none found")
    if os.environ.get("REANA_SERVER_URL") and os.environ.get("REANA_ACCESS_TOKEN"):
        print("\nConnectivity check:")
        return run_reana(["ping"]).returncode
    return 0


def cmd_client(_: argparse.Namespace) -> int:
    print("REANA client selection:")
    print(f"  requested mode: {client_mode()}")
    print(f"  selected client: {selected_client()}")
    print(f"  native reana-client: {native_client() or '<not found>'}")
    docker = docker_client()
    print(f"  docker: {docker or '<not found>'}")
    if docker:
        ok, msg = check_docker_daemon(docker)
        print(f"  docker daemon: {'available' if ok else 'unavailable'}{(': ' + msg) if msg else ''}")
    print(f"  Docker image: {client_image()}")
    print(f"  REANA_SERVER_URL: {os.environ.get('REANA_SERVER_URL', '<unset>')}")
    print(f"  Token configured: {'yes' if os.environ.get('REANA_ACCESS_TOKEN') else 'no'}")
    return 0


def cmd_recent(ns: argparse.Namespace) -> int:
    data = load_json_list()
    statuses = normalize_status_filter(ns.status)
    rows: list[list[str]] = []
    for item in data:
        status = row_value(item, "status").lower()
        if statuses and status not in statuses:
            continue
        rows.append([
            row_value(item, "name"),
            row_value(item, "run_number", "run"),
            row_value(item, "status"),
            row_value(item, "created", "created_at", "started"),
            row_value(item, "duration"),
            row_value(item, "id", "workflow_id"),
        ])
        if len(rows) >= ns.limit:
            break
    print_table(rows, ["name", "run", "status", "created", "duration", "id"])
    return 0


def cmd_status(ns: argparse.Namespace) -> int:
    return run_reana(["status", "-w", ns.workflow]).returncode


def cmd_logs(ns: argparse.Namespace) -> int:
    cp = run_reana(["logs", "-w", ns.workflow], capture=True)
    out = cp.stdout or ""
    lines = out.splitlines()
    if ns.tail and len(lines) > ns.tail:
        lines = lines[-ns.tail:]
    print("\n".join(lines))
    if cp.stderr.strip():
        print(cp.stderr.strip(), file=sys.stderr)
    return cp.returncode


def cmd_download(ns: argparse.Namespace) -> int:
    out = Path(ns.out)
    out.mkdir(parents=True, exist_ok=True)
    return run_reana(["download", "-w", ns.workflow, "-o", str(out)]).returncode


def slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-._").lower()
    return value or "reana-job"


def detect_command(project: Path, script: str | None, command: str | None) -> tuple[list[str], list[str]]:
    inputs: list[str] = []
    if command:
        return [f"bash -lc {shlex.quote(command)}"], inputs
    if script:
        inputs.append(script)
        if script.endswith(".py"):
            install = "if [ -f requirements.txt ]; then pip install --quiet -r requirements.txt; fi"
            return [f"bash -lc {shlex.quote(f'{install} && python3 {shlex.quote(script)}')}"], inputs
        if script.endswith(".sh"):
            return [f"bash -lc {shlex.quote(f'bash {shlex.quote(script)}')}"], inputs
        return [f"bash -lc {shlex.quote(f'./{shlex.quote(script)}')}"], inputs
    if (project / "analysis.py").exists():
        inputs.append("analysis.py")
        return ["bash -lc 'if [ -f requirements.txt ]; then pip install --quiet -r requirements.txt; fi && python3 analysis.py'"], inputs
    if (project / "run.sh").exists():
        inputs.append("run.sh")
        return ["bash -lc 'bash run.sh'"], inputs
    return ["bash -lc 'echo Hello REANA | tee output.txt'"], inputs


def write_reana_yaml(project: Path, workflow_name: str, commands: list[str], inputs: list[str], outputs: list[str], environment: str, timeout: int) -> None:
    files = []
    for item in inputs:
        if item not in files:
            files.append(item)
    if (project / "requirements.txt").exists() and "requirements.txt" not in files:
        files.append("requirements.txt")
    lines = ["version: 0.9.0"]
    if files:
        lines += ["inputs:", "  files:"] + [f"    - {f}" for f in files]
    lines += [
        "workflow:",
        "  type: serial",
        "  specification:",
        "    steps:",
        f"      - name: {workflow_name}",
        f"        environment: {environment}",
        "        kubernetes_memory_limit: \"32Gi\"",
        f"        kubernetes_job_timeout: {timeout}",
        "        compute_backend: kubernetes",
        "        commands:",
    ]
    lines += [f"          - {cmd}" for cmd in commands]
    if outputs:
        lines += ["outputs:", "  files:"] + [f"    - {o}" for o in outputs]
    (project / "reana.yaml").write_text("\n".join(lines) + "\n")


def write_ignore(project: Path) -> None:
    ignore = project / ".reanaignore"
    if ignore.exists():
        return
    ignore.write_text("""# Files that should not be uploaded to REANA workspaces\n.git/\n.env\n.reana/\n__pycache__/\n*.pyc\n*.pyo\n.ipynb_checkpoints/\n.DS_Store\n*.pem\n*.key\n*token*\n*secret*\n*password*\n""")


def cmd_scaffold(ns: argparse.Namespace) -> int:
    project = Path(ns.project).resolve()
    project.mkdir(parents=True, exist_ok=True)
    workflow = slugify(ns.workflow or project.name)
    script = ns.script
    if ns.code:
        script = script or "analysis.py"
        target = project / script
        if target.exists() and not ns.force:
            fail(f"Refusing to overwrite existing {target}; pass --force")
        target.write_text(ns.code.rstrip() + "\n")
    elif script and not (project / script).exists():
        if script.endswith(".py"):
            (project / script).write_text("print('Hello from REANA')\nopen('output.txt', 'w').write('Hello from REANA\\n')\n")
        elif script.endswith(".sh"):
            (project / script).write_text("#!/usr/bin/env bash\nset -euo pipefail\necho 'Hello from REANA' | tee output.txt\n")
        else:
            fail(f"Script {script} does not exist in {project}")
    commands, inputs = detect_command(project, script, ns.command)
    outputs = ns.output or ["output.txt"]
    write_reana_yaml(project, workflow, commands, inputs, outputs, ns.environment, ns.timeout)
    write_ignore(project)
    print(f"Created/updated REANA project: {project}")
    print(f"Workflow: {workflow}")
    print("Files:")
    for p in [project / "reana.yaml", project / ".reanaignore"] + ([project / script] if script else []):
        if p.exists():
            print(f"  {p}")
    print("Next:")
    print(f"  {Path(__file__).name} validate --project {shlex.quote(str(project))}")
    print(f"  {Path(__file__).name} run --project {shlex.quote(str(project))} --workflow {shlex.quote(workflow)}")
    return 0


def parse_reana_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception:
        fail("PyYAML is required for validate/scaffold")
    try:
        data = yaml.safe_load(path.read_text()) or {}
    except Exception as exc:
        fail(f"Invalid YAML in {path}: {exc}")
    if not isinstance(data, dict):
        fail(f"{path} must parse as a YAML mapping")
    return data


def iter_input_files(data: dict[str, Any]) -> Iterable[str]:
    inputs = data.get("inputs") or {}
    if isinstance(inputs, dict):
        files = inputs.get("files") or []
        if isinstance(files, list):
            yield from [str(x) for x in files]
    elif isinstance(inputs, list):
        for item in inputs:
            if isinstance(item, dict) and item.get("path"):
                yield str(item["path"])


def cmd_validate(ns: argparse.Namespace) -> int:
    project = Path(ns.project).resolve()
    path = project / "reana.yaml"
    if not path.exists():
        fail(f"Missing {path}")
    data = parse_reana_yaml(path)
    problems: list[str] = []
    for f in iter_input_files(data):
        if not (project / f).exists():
            problems.append(f"input file listed but missing: {f}")
    text = path.read_text()
    if "REANA_ACCESS_TOKEN" in text or "access_token" in text.lower():
        problems.append("reana.yaml appears to contain token/access-token text; keep credentials in environment variables")
    if "kubernetes_memory_limit" not in text and "memory: 32" not in text.lower() and "memory: 32gb" not in text.lower():
        problems.append("no obvious 32Gi/32gb memory setting found")
    if "outputs:" not in text:
        problems.append("no outputs declared")
    if "cat <<" in text:
        problems.append("inline heredoc detected; use separate script files instead")
    if problems:
        print("Validation FAILED:")
        for p in problems:
            print(f"- {p}")
        return 1
    print(f"Validation PASS: {path}")
    return 0


def cmd_run(ns: argparse.Namespace) -> int:
    project = Path(ns.project).resolve()
    rc = cmd_validate(argparse.Namespace(project=str(project)))
    if rc != 0:
        return rc
    workflow = slugify(ns.workflow or project.name)
    if ns.timestamp:
        workflow = f"{workflow}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    print(f"Server: {os.environ.get('REANA_SERVER_URL', '<unset>')}")
    print(f"Workflow: {workflow}")
    yaml_arg = "/workspace/reana.yaml" if selected_client() == "docker" else "reana.yaml"
    cp = run_reana(["run", "-w", workflow, "-f", yaml_arg], mount=project)
    print("Next useful commands:")
    print(f"  status:   {Path(__file__).name} status {workflow}")
    print(f"  logs:     {Path(__file__).name} logs {workflow} --tail 100")
    print(f"  download: {Path(__file__).name} download {workflow} --out outputs/{workflow}")
    return cp.returncode


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Operate REANA jobs using REANA_SERVER_URL and REANA_ACCESS_TOKEN from the environment.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ping", help="Check REANA connectivity").set_defaults(func=cmd_ping)
    sub.add_parser("client", help="Show native-vs-Docker client selection and failover diagnostics").set_defaults(func=cmd_client)
    sub.add_parser("backends", help="Show active server, client mode, and known local profiles").set_defaults(func=cmd_backends)
    r = sub.add_parser("recent", help="List recent workflows, optionally filtered by status")
    r.add_argument("--status", help="Status alias: failed, running, pending, success/finished, stopped")
    r.add_argument("--limit", type=int, default=10)
    r.set_defaults(func=cmd_recent)
    s = sub.add_parser("status", help="Show workflow status")
    s.add_argument("workflow")
    s.set_defaults(func=cmd_status)
    l = sub.add_parser("logs", help="Show workflow logs")
    l.add_argument("workflow")
    l.add_argument("--tail", type=int, default=100)
    l.set_defaults(func=cmd_logs)
    d = sub.add_parser("download", help="Download workflow outputs")
    d.add_argument("workflow")
    d.add_argument("--out", default="outputs")
    d.set_defaults(func=cmd_download)
    sc = sub.add_parser("scaffold", help="Create/update a REANA project with reana.yaml")
    sc.add_argument("--project", required=True)
    sc.add_argument("--workflow")
    sc.add_argument("--script", help="Script filename inside project, e.g. analysis.py or run.sh")
    sc.add_argument("--code", help="Inline code to write into --script, usually for quick Python jobs")
    sc.add_argument("--command", help="Explicit shell command to run in REANA instead of script detection")
    sc.add_argument("--output", action="append", help="Output file to declare; repeatable")
    sc.add_argument("--environment", default=DEFAULT_ENVIRONMENT)
    sc.add_argument("--timeout", type=int, default=7200)
    sc.add_argument("--force", action="store_true")
    sc.set_defaults(func=cmd_scaffold)
    v = sub.add_parser("validate", help="Validate project reana.yaml before submission")
    v.add_argument("--project", required=True)
    v.set_defaults(func=cmd_validate)
    run = sub.add_parser("run", help="Validate and submit a project to REANA")
    run.add_argument("--project", required=True)
    run.add_argument("--workflow")
    run.add_argument("--timestamp", action="store_true", help="Append UTC timestamp to workflow name")
    run.set_defaults(func=cmd_run)
    return p


def main(argv: list[str] | None = None) -> int:
    ns = build_parser().parse_args(argv)
    return int(ns.func(ns) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
