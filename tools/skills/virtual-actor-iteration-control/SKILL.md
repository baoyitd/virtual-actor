---
name: virtual-actor-iteration-control
description: Use when starting or checking a virtual-actor product iteration, tightening design/test/delivery alignment, recording implementation drift, or preparing an acceptance or release handoff for this repo.
---

# virtual-actor Iteration Control

Use this skill for the `virtual-actor` repo when work involves:

1. starting a new product version
2. changing product scope, UI/UX, backend behavior, integration behavior, or delivery evidence
3. checking whether design, implementation, tests, release notes, and `portfolio-sync.md` still align
4. preparing to ask for user acceptance or to claim a Formal Status upgrade

## Required Workflow

### 1. Before implementation

- Read `docs/iterations/current.txt`.
- Ensure the active dossier exists:
  - `scope.md`
  - `design-delta.md`
  - `implementation-notes.md`
  - `traceability.md`
- If starting a new version, run:

```bash
python3 scripts/init_iteration_version.py <version> --repo-root . --set-current
```

- Do not implement until `Scope In`, `Scope Out`, user scenarios, tests, and stop conditions are clear.

### 2. During implementation

- If scope expands, interfaces change, fields are insufficient, or UI paths differ from the plan, stop and update the active dossier first.
- Record expected vs actual behavior in `implementation-notes.md`.
- If the problem reflects a process gap, append it to `docs/process/issue-and-optimization-log.md`.

### 3. Before acceptance or release claims

Run:

```bash
npm run lint:md
vale delivery docs portfolio-sync.md
python3 scripts/iteration-guard.py --repo-root . --mode release
```

Then check:

- `delivery/test-plan.md`, `delivery/test-results.md`, `delivery/release-notes.md`, `portfolio-sync.md`, and the active dossier agree on version, scope, and Formal Status.
- `Accepted` requires manual smoke evidence for high-risk user paths.
- `real integration` is not used for mock, stub, static fixture, or manual fixture evidence.
- Knowledge platform Accepted scope is not written as a long-term frozen public contract.
- Decision product integration is not claimed unless separately planned and accepted.

## Project Defaults

- Current accepted baseline: `v0.3.0-commercial-trial`, Formal Status `Accepted`.
- Current active iteration: read from `docs/iterations/current.txt`, initially `v0.4.0`.
- Formal Status values are only `Draft`, `Self-Tested`, `User-Acceptance-Candidate`, and `Accepted`.
- This project is a FastAPI + React code repo, not a Markdown/Vault true-source project; do not use knowledge-workbench `quality-check.py`.

## Expected Output

- A version dossier that can drive implementation without hidden decisions.
- Recorded implementation deviations when reality differs from design.
- Delivery evidence that matches the actual verified scope before any acceptance or release claim.
