# TESGI Advisory Project Instructions

Version: 2.1-Agentic
Status: Active

## 1. Purpose

TESGI delivers non-representational advisory analysis for land and property decisions.
The required decision states are `Proceed`, `Pause`, or `Avoid`.

## 2. Canonical Decision Kernel

All advisory reasoning must pass:

- `TRUE`: material facts are verifiable, available, and bounded.
- `NORTH`: decision remains coherent over time and constraints.
- `ALIGNED`: objectives, assumptions, and structure fit.

Any leg failure requires `Pause` or `Avoid`.

## 3. Active Workspace Model

`TESGI_Claudvisor/` is the Claude-side workspace.
Canonical packaging, gates, and orchestration run in `tesgi-advisory-os/`.
The adapter bridge is the contract between both workspaces.

Key paths:

- Claude client work: `TESGI_Claudvisor/clients/<client_id>/`
- TESGI client work: `tesgi-advisory-os/02_client_work/<slug>/`
- Mapping contract: `tesgi-advisory-os/03_tools/adapter/MAPPING_SPEC.md`
- Coordination log: `Coordination_Inbox/codex_claude_changelog.md`

## 4. Standard Operating Flow

1. Run Claude commands to produce intake, analysis, sources, and memo drafts.
2. Sync Claude to TESGI:
   - `python 03_tools/adapter/claude_to_tesgi.py <client_id> --force`
3. Run TESGI command chain:
   - `python -m tesgi validate <slug>`
   - `python -m tesgi build-memo <slug>`
   - `python -m tesgi package <slug>`
   - `python -m tesgi run <slug>`
4. If needed, sync TESGI back to Claude:
   - `python 03_tools/adapter/tesgi_to_claude.py <slug> --force`
5. Run regression checks before governance-sensitive changes:
   - `python -m tesgi eval`
   - `python -m tesgi eval --include-negative`

## 5. Packaging and Evidence Requirements

Required package artifacts in `04_package/`:

- `memo.pdf`
- `invoice.pdf`
- `receipt.pdf`
- `manifest.json`
- `gate_report.json`
- `runlog.jsonl`

Run outputs in `runs/YYYYMMDD_<slug>_<run_id>/` must include:

- `manifest.json`
- `gate_report.json`
- `build_log.txt`
- `codex_session_pointer.txt`

## 6. Boundary and Language Discipline

- Advisory only; no representation.
- No guarantees or outcome promises.
- Decision memo must include "What This Memo Does Not Say".
- Decision memo must include "Non-representational advisory only".

## 7. Change Control

- Follow TESGI tiered governance in `tesgi-advisory-os/00_governance/CHANGE_CONTROL.md`.
- Constitution-level changes require ADR and explicit acceptance.
- `ADR_0001_Governed_Self_Improvement.md` is the baseline governance ADR.

## 8. Deprecated References

Do not use `scripts/validate_kernel.py`; it is not part of the active architecture.
Use `python -m tesgi validate <slug>` for gate validation.

## 9. Coordination Requirement

After substantial changes, append a concise entry to:

- `Coordination_Inbox/codex_claude_changelog.md`

This file is the shared cross-agent handoff record.
