---
name: kanban-worker
title: Kanban Multi-Agent Workflow — Orchestrator Playbook + Worker Pitfalls
description: >-
  Complete guide to the Hermes Kanban system: the orchestrator decomposition
  playbook, specialist roster conventions, anti-temptation rules, and the deeper
  worker pitfalls, examples, and edge cases. The core lifecycle is auto-injected
  into every worker's system prompt; load this skill for full detail.
author: Hermes Agent
date: 2026-04-30
tags: [kanban, multi-agent, orchestration, workflow, pitfalls, routing]
---

# Kanban Multi-Agent Workflow

This umbrella covers the complete Kanban system: the orchestrator role (decompose,
route, summarize) and the worker role (workspace handling, handoffs, retries).

## Part 1: Orchestrator Playbook

> The **core worker lifecycle** is auto-injected via the `KANBAN_GUIDANCE` system-prompt
> block. This skill is the deeper playbook.

### When to use the board (vs. just doing the work)

Create Kanban tasks when any of these are true:
1. **Multiple specialists are needed** — research + analysis + writing is three profiles.
2. **The work should survive a crash or restart** — long-running, recurring, or important.
3. **The user might want to interject** — human-in-the-loop at any step.
4. **Multiple subtasks can run in parallel** — fan-out for speed.
5. **Review / iteration is expected** — a reviewer profile loops on drafter output.
6. **The audit trail matters** — board rows persist in SQLite forever.

If *none* of those apply — use `delegate_task` instead or answer directly.

### The anti-temptation rules

- **Do not execute the work yourself.** Your restricted toolset usually doesn't include
  terminal/file/code/web for implementation.
- **For any concrete task, create a Kanban task and assign it.** Every single time.
- **If no specialist fits, ask the user which profile to create.**
- **Decompose, route, and summarize — that's the whole job.**

### Standard specialist roster

| Profile | Does | Workspace |
|---|---|---|
| `researcher` | Reads sources, gathers facts, writes findings | `scratch` |
| `analyst` | Synthesizes, ranks, de-dupes | `scratch` |
| `writer` | Drafts prose in the user's voice | `scratch` or vault |
| `reviewer` | Reads output, leaves findings, gates approval | `scratch` |
| `backend-eng` | Writes server-side code | `worktree` |
| `frontend-eng` | Writes client-side code | `worktree` |
| `ops` | Runs scripts, manages services, deployments | ops scripts repo |
| `pm` | Writes specs, acceptance criteria | `scratch` |

### Decomposition playbook

**Step 1** — Understand the goal. Ask clarifying questions if ambiguous.
**Step 2** — Sketch the task graph in your response. Show to the user before creating anything.
**Step 3** — Create tasks with `kanban_create`, link with `parents=[...]`.
**Step 4** — If you were spawned as a task yourself, mark it done with a summary.
**Step 5** — Report back to the user in plain prose.

### Common patterns

- **Fan-out + fan-in:** N `researcher` tasks → one `analyst` task with all as parents.
- **Pipeline with gates:** `pm → backend-eng → reviewer`. Reviewer blocks or completes.
- **Same-profile queue:** many tasks, all to one profile, no dependencies.
- **Human-in-the-loop:** Any task can `kanban_block()` to wait for input.
- **Paper/document pipeline:** N parallel READ-ONLY audit tasks (consistency/flow, bibliography, figure QA) → one revise task with all audits as parents (backup git branch before any edit) → build gate → human-approval gate → package/publish. Marking audits read-only in their briefs is what makes them safe to parallelize on a shared `dir:` workspace. Subscribe platform notifications on the gate + package tasks. Worked example: drp-paper skill, `references/kanban-board-2026-07-04.md`.\n- **Human-gate task:** brief the worker to post a review digest comment, then `kanban_block` with a specific approval question — blocking IS the deliverable; the task must NOT complete itself. On approval → unblock; on change requests → create a NEW revision task looping back through the build gate.

### Orchestrator pitfalls

- **Reassignment vs. new task:** If a reviewer blocks, create a NEW task — don't re-run the same task.
- **Argument order:** `kanban_link(parent_id=..., child_id=...)` — parent first.
- **Don't pre-create the whole graph if the shape depends on intermediate findings.**

### Running boards with the CLI daemon (host-side ops)

Monitor: `hermes kanban --board <b> list | show <id> | tail <id> | log <id>` — `show` gives summary+comments+events, `log` gives the worker's live tool-call trace (most informative for "what is it doing NOW"), `tail` streams events only.

- **Daemon liveness:** check with `pgrep -F <pidfile>` before assuming tasks will progress — the daemon can die silently, leaving a stale pidfile and a board stuck in `todo`. Restart via `terminal(background=true)` (Hermes rejects foreground `&` backgrounding); `rm -f` the stale pidfile first.
- **Timeouts are cheap IF workers commit incrementally.** A revise worker hitting `max_runtime_seconds` (timed_out) is auto-requeued; the next run resumes from the last commit. Brief long edit workers to commit after each coherent fix batch — then a timeout costs minutes, not the run. (Observed: run timed out at 2703s with 2 commits landed; next run verified they compile and continued seamlessly.)
- **Approving a human-gate from chat:** when the user approves in conversation instead of via the worker's channel, the parent agent records it directly: `hermes kanban --board <b> comment <gate_id> "APPROVED by <user>: <what was resolved>"` then `complete <gate_id> --summary "..."` — the daemon promotes the downstream task on the next tick. Same pattern for deferred items the gate listed: do the fixes, comment the resolution on the gate card (audit trail), then complete.
- **Packaging tasks should verify standalone:** brief them to extract the actual built tarball into a clean temp dir and compile/run from THAT — not from the repo — and report checksums + page counts as evidence.

---

## Part 2: Worker Pitfalls and Examples

### Workspace handling

| Kind | What it is | How to work |
|---|---|---|
| `scratch` | Fresh tmp dir, yours alone | Read/write freely; GC'd when task archived |
| `dir:<path>` | Shared persistent directory | Treat like long-lived state |
| `worktree` | Git worktree at resolved path | Commit work here; ensure `.git` exists first |

### Good summary + metadata shapes

**Coding task:**
```python
kanban_complete(
    summary="shipped rate limiter — token bucket, keys on user_id with IP fallback, 14 tests pass",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14, "tests_passed": 14,
        "decisions": ["user_id primary, IP fallback for unauthenticated"],
    },
)
```

**Research task:**
```python
kanban_complete(
    summary="3 competing libraries reviewed; vLLM wins on throughput, SGLang on latency",
    metadata={
        "sources_read": 12, "recommendation": "vLLM",
        "benchmarks": {"vllm": 1.0, "sglang": 0.87, "trtllm": 0.72},
    },
)
```

**Review task:**
```python
kanban_complete(
    summary="reviewed PR #123; 2 blocking issues (SQL injection in /search, missing CSRF on /settings)",
    metadata={
        "pr_number": 123, "approved": False,
        "findings": [{"severity": "critical", "file": "api/search.py", "issue": "raw SQL concat"}],
    },
)
```

### Block reasons that get answered fast

Bad: `"stuck"` — the human has no context.
Good: one sentence naming the specific decision needed. Leave longer context as a comment.

### Heartbeats worth sending

Good: `"epoch 12/50, loss 0.31"`, `"scanned 1.2M/2.4M rows"`.
Bad: `"still working"`, empty notes, sub-second intervals.

### Retry diagnostics

| Prior outcome | What it means | What to do |
|---|---|---|
| `timed_out` | Hit `max_runtime_seconds` | Chunk the work or shorten it |
| `crashed` | OOM or segfault | Reduce memory footprint |
| `spawn_failed` | Profile config issue (missing credential) | Ask via `kanban_block` |
| `reclaimed` | Task archived out from under previous run | Check status carefully |
| `blocked` | Previous attempt blocked | Unblock comment should be in thread |

### Do NOT

- Call `delegate_task` as substitute for `kanban_create`
- Modify files outside `$HERMES_KANBAN_WORKSPACE`
- Create follow-up tasks assigned to yourself
- Complete a task you didn't actually finish

### Workspace pitfalls

- Task state can change between dispatch and startup — always `kanban_show` first
- Workspace may have stale artifacts from previous runs — read the comment thread
- Use the `kanban_*` tools, not the CLI — the CLI isn't installed in containerized backends
