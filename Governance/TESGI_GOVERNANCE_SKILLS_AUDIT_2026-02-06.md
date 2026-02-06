# TESGI Governance and Skills Audit

Date: 2026-02-06  
Scope: TESGI Duo Advisory operations (Codex + Claude)

## Audit Scope

- Governance baseline in `tesgi-advisory-os/00_governance/`
- Gate and eval enforcement in `tesgi-advisory-os`
- Installed operational skills in:
  - `TESGI_Claudvisor/skills/`
  - `C:/Users/Chad/.codex/skills/` (non-system skills)
- Canonical lock artifact:
  - `Governance/TESGI_CANONICAL_SKILL_BUNDLE_v1.0.lock.json`

## Evidence Collected

- Governance files present and readable:
  - `tesgi-advisory-os/00_governance/KERNEL.md`
  - `tesgi-advisory-os/00_governance/BOUNDARIES.md`
  - `tesgi-advisory-os/00_governance/LANGUAGE_RULES.yml`
  - `tesgi-advisory-os/00_governance/CHANGE_CONTROL.md`
  - `tesgi-advisory-os/00_governance/PLUGIN_ALLOWLIST.json`
- Runtime validation:
  - `python -m tesgi validate demo` -> PASS (O, A, B, C, D, E)
  - `python -m tesgi eval --include-negative` -> PASS (14 cases, 8 expected failures)
  - `python 03_tools/plugins/list_allowlisted_plugins.py` -> PASS
- Repository baselines at audit time:
  - Root coordination repo: `31243ea`
  - `tesgi-advisory-os`: `ba2704d`
  - `TESGI_Claudvisor`: `4709670`

## Findings

## Critical

- None.

## High

- None.

## Medium

- Operational drift risk: `tesgi-advisory-os/runs/20260206_demo_071022Z/` is untracked runtime output.
  - Impact: can create noisy diffs and confusion if treated as canonical artifact.
  - Control: keep run outputs excluded from governance baselines.

## Low

- Coordination workspace has ongoing human-managed edits in `Coordination_Inbox/`.
  - Impact: expected and acceptable for cross-agent handoff, but not a normative source of truth.
  - Control: keep canonical governance in `tesgi-advisory-os/00_governance/` and lock file.

## Audit Conclusion

Governance controls are operational and passing current validation/eval thresholds.  
The skill estate is now captured as a hash-locked v1.0 baseline in:

- `Governance/TESGI_CANONICAL_SKILL_BUNDLE_v1.0.lock.json`

This is suitable to enforce a stable TESGI Advisory operating standard, provided bundle changes remain under explicit human approval.

