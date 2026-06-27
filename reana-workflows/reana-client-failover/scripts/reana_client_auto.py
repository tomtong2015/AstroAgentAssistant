#!/usr/bin/env python3
"""Token-safe REANA client launcher with native-to-Docker failover.

Selection policy:
- REANA_CLIENT_MODE=auto (default): native reana-client first, Docker fallback.
- REANA_CLIENT_MODE=native: require native reana-client.
- REANA_CLIENT_MODE=docker: force Dockerized reanahub/reana-client.

Credentials are passed via REANA_SERVER_URL and REANA_ACCESS_TOKEN and never printed.
"""
from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_IMAGE = "reanahub/reana-client:0.95.0-alpha.3"
VALID_MODES = {"auto", "native", "docker"}


def fail(message: str, code: int = 2) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def client_mode() -> str:
    mode = os.environ.get("REANA_CLIENT_MODE", "auto").strip().lower() or "auto"
    if mode not in VALID_MODES:
        fail(f"Invalid REANA_CLIENT_MODE={mode!r}; expected one of: {', '.join(sorted(VALID_MODES))}")
    return mode


def client_image() -> str:
    return os.environ.get("REANA_CLIENT_IMAGE", DEFAULT_IMAGE)


def native_client() -> str | None:
    return shutil.which("reana-client")


def docker_client() -> str | None:
    return shutil.which("docker")


def check_docker_daemon(docker: str) -> tuple[bool, str]:
    cp = subprocess.run([docker, "version", "--format", "{{.Server.Version}}"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cp.returncode == 0:
        return True, cp.stdout.strip() or "available"
    return False, (cp.stderr or cp.stdout).strip()


def selected_backend() -> str:
    mode = client_mode()
    native = native_client()
    docker = docker_client()
    if mode == "native":
        if not native:
            fail("REANA_CLIENT_MODE=native but reana-client was not found on PATH")
        return "native"
    if mode == "docker":
        if not docker:
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


def require_reana_env() -> None:
    missing = [k for k in ["REANA_SERVER_URL", "REANA_ACCESS_TOKEN"] if not os.environ.get(k)]
    if missing:
        fail("Set required environment variables first: " + ", ".join(missing))


def normalize_args_for_backend(args: list[str], backend: str, project: Path | None) -> list[str]:
    if backend != "docker" or not project:
        return args
    # Users naturally pass -f reana.yaml. Inside the container, that project is /workspace.
    out: list[str] = []
    i = 0
    while i < len(args):
        token = args[i]
        if token in {"-f", "--file"} and i + 1 < len(args):
            value = args[i + 1]
            if not value.startswith("/"):
                value = "/workspace/" + value
            out.extend([token, value])
            i += 2
            continue
        out.append(token)
        i += 1
    return out


def build_command(args: list[str], project: Path | None = None) -> tuple[list[str], Path | None, str]:
    require_reana_env()
    backend = selected_backend()
    if backend == "native":
        native = native_client()
        if native is not None:
            cwd = project.resolve() if project else None
            return [native, *args], cwd, backend
        fail("reana-client disappeared from PATH")

    docker = docker_client()
    if not docker:
        fail("docker disappeared from PATH")
    docker_args = [docker, "run", "--rm", "-e", "REANA_SERVER_URL", "-e", "REANA_ACCESS_TOKEN"]
    normalized = normalize_args_for_backend(args, "docker", project)
    if project:
        mount = project.resolve()
        if not mount.exists():
            fail(f"Project directory does not exist: {mount}")
        docker_args += ["-v", f"{mount}:/workspace", "-w", "/workspace"]
    docker_args += [client_image(), *normalized]
    return docker_args, None, backend


def printable_command(cmd: list[str], cwd: Path | None = None) -> str:
    text = " ".join(shlex.quote(x) for x in cmd)
    if cwd:
        return f"(cd {shlex.quote(str(cwd))} && {text})"
    return text


def run_client(args: list[str], project: Path | None = None) -> int:
    cmd, cwd, backend = build_command(args, project=project)
    print(f"Client mode: {backend}")
    print(f"$ {printable_command(cmd, cwd)}")
    return subprocess.run(cmd, text=True, cwd=cwd).returncode


def cmd_doctor(_: argparse.Namespace) -> int:
    mode = client_mode()
    native = native_client()
    docker = docker_client()
    print("REANA client failover doctor")
    print(f"  requested mode: {mode}")
    print(f"  REANA_SERVER_URL: {os.environ.get('REANA_SERVER_URL', '<unset>')}")
    print(f"  Token configured: {'yes' if os.environ.get('REANA_ACCESS_TOKEN') else 'no'}")
    print(f"  REANA_CLIENT_IMAGE: {client_image()}")
    print(f"  native reana-client: {native or '<not found>'}")
    if native:
        cp = subprocess.run([native, "--version"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        version = cp.stdout.strip().splitlines()
        if version:
            print(f"  native version: {version[0]}")
    print(f"  docker: {docker or '<not found>'}")
    if docker:
        ok, msg = check_docker_daemon(docker)
        print(f"  docker daemon: {'available' if ok else 'unavailable'}{(': ' + msg) if msg else ''}")
    try:
        print(f"  selected client: {selected_backend()}")
    except SystemExit as exc:
        return int(exc.code or 2)
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run REANA client commands with native-to-Docker failover. Use 'doctor' for diagnostics."
    )
    parser.add_argument("--project", help="Workflow project directory for commands that upload local files, e.g. run -f reana.yaml")
    parser.add_argument("reana_args", nargs=argparse.REMAINDER, help="REANA command and arguments, e.g. ping or run -w wf -f reana.yaml")
    ns = parser.parse_args(argv)
    if not ns.reana_args:
        parser.print_help()
        raise SystemExit(0)
    if ns.reana_args and ns.reana_args[0] == "--":
        ns.reana_args = ns.reana_args[1:]
    return ns


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv)
    if ns.reana_args == ["doctor"]:
        return cmd_doctor(ns)
    project = Path(ns.project).resolve() if ns.project else None
    if project and not project.exists():
        fail(f"Project directory does not exist: {project}")
    return run_client(ns.reana_args, project=project)


if __name__ == "__main__":
    raise SystemExit(main())
