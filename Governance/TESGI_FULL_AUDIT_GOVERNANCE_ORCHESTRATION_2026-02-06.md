# TESGI Full System Audit: Governance and Orchestration Architecture

Date: 2026-02-06  
Auditor: Codex (GPT-5)  
Scope: `tesgi-advisory-os`, `TESGI_Claudvisor`, and coordination-layer governance artifacts

## Executive Summary

Current state is operational and materially improved: core gates run, regression coverage includes expected-fail negatives, plugin loading is allowlisted/version-pinned, and Claude/TESGI adapters are present.

The main remaining risk is **spec parity drift**. The implementation currently enforces a stable subset of the architecture, but key parts of `TESGI_Advisory_Spec_v01.md` are still not implemented as written (notably command/package surface and governance baseline artifacts).

Overall rating: **Amber** (operationally stable, not yet fully spec-conformant).

## Evidence Run Log

Validated during this audit:

- `python -m tesgi --help` -> PASS
- `python -m tesgi validate demo` -> PASS
- `python -m tesgi eval` -> PASS (6 cases)
- `python -m tesgi eval --include-negative` -> PASS (14 cases, 8 expected failures)
- `python -m tesgi validate demo --plugins all` -> PASS
- `python -m tesgi eval --include-negative --plugins all` -> PASS
- `python 03_tools/orchestration/states.py` -> PASS
- `python 03_tools/orchestration/engine.py demo` -> PASS
- `python 03_tools/plugins/list_allowlisted_plugins.py` -> PASS
- `python 03_tools/adapter/claude_to_tesgi.py --help` -> PASS
- `python 03_tools/adapter/tesgi_to_claude.py --help` -> PASS
- `python -m tesgi run demo` -> PASS

## Architecture Baseline (As-Is)

Governance core:

- `tesgi-advisory-os/00_governance/KERNEL.md`
- `tesgi-advisory-os/00_governance/BOUNDARIES.md`
- `tesgi-advisory-os/00_governance/LANGUAGE_RULES.yml`
- `tesgi-advisory-os/00_governance/CHANGE_CONTROL.md`
- `tesgi-advisory-os/00_governance/PLUGIN_ALLOWLIST.json`

Orchestration implementation:

- Single CLI orchestrator and gate execution in `tesgi-advisory-os/tesgi/__main__.py:587`
- State model in `tesgi-advisory-os/tesgi/orchestration/states.py:7`
- Stage contracts in `tesgi-advisory-os/tesgi/orchestration/contracts.py:31`
- Runtime orchestration engine in `tesgi-advisory-os/tesgi/orchestration/engine.py:34`

Plugin architecture:

- Interfaces in `tesgi-advisory-os/tesgi/plugins/interfaces.py:9`
- Allowlist loader/runtime manager in `tesgi-advisory-os/tesgi/plugins/manager.py:41`
- Reference plugins in `tesgi-advisory-os/tesgi/plugins/reference.py:17`

Cross-agent adapters:

- Mapping spec in `tesgi-advisory-os/03_tools/adapter/MAPPING_SPEC.md`
- Claude -> TESGI sync in `tesgi-advisory-os/03_tools/adapter/claude_to_tesgi.py:119`
- TESGI -> Claude sync in `tesgi-advisory-os/03_tools/adapter/tesgi_to_claude.py:107`

Canonical locked skill baseline:

- `Governance/TESGI_CANONICAL_SKILL_BUNDLE_v1.0.lock.json`

## Findings (Ordered by Severity)

## Critical

1. Spec-required command and package surfaces are not fully implemented.
- Spec requires `tesgi build-memo <slug>` and `tesgi package <slug>` in addition to `run`: `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:270`, `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:272`, `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:274`.
- Actual CLI exposes only `init-client`, `validate`, `run`, `eval`: `tesgi-advisory-os/tesgi/__main__.py:950`.
- Spec package structure requires `memo.pdf`, `invoice.pdf`, `receipt.pdf`, and `runlog.jsonl (or pointer)`: `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:159`, `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:160`, `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:161`, `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:163`.
- Current integrity allowlist and run outputs are manifest/gate-report centric only: `tesgi-advisory-os/tesgi/__main__.py:15`, `tesgi-advisory-os/tesgi/__main__.py:22`, `tesgi-advisory-os/tesgi/__main__.py:23`, `tesgi-advisory-os/tesgi/__main__.py:734`, `tesgi-advisory-os/tesgi/__main__.py:744`.
- Impact: system passes internal gates while still below declared deliverable spec.

## High

2. Required governance bootstrap ADR is missing.
- Spec requires `ADR_0001_Governed_Self_Improvement.md`: `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:134`.
- Only template exists: `tesgi-advisory-os/00_governance/ADR/ADR_TEMPLATE.md`.
- Impact: formal constitutional baseline is implied but not materially present.

3. Gate A semantic depth is still below v0.1 spec wording.
- Spec requires explicit content categories: observations, explicit uncertainties, risk notes: `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:204`, `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:206`, `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:208`.
- Current Gate A checks heading aliases + a `Status:` line: `tesgi-advisory-os/tesgi/__main__.py:26`, `tesgi-advisory-os/tesgi/__main__.py:360`, `tesgi-advisory-os/tesgi/__main__.py:396`.
- Impact: structurally valid but semantically weak analysis can still pass.

4. Change-control tier taxonomy drifts from the spec framing.
- Spec frames constitution/kernel changes as Tier C: `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:77`, `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:81`.
- Current governance file labels kernel files as Tier A: `tesgi-advisory-os/00_governance/CHANGE_CONTROL.md:5`.
- Impact: reviewers can misclassify risk and approval strictness.

5. Orchestration contracts are partially inconsistent with "all gates" semantics, and stage schemas are not enforced at runtime.
- Spec: package cannot be produced unless all gates pass: `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:192`.
- `package_passed` contract omits `O` and `E`: `tesgi-advisory-os/tesgi/orchestration/contracts.py:66`.
- `eval_passed` contract omits `O`: `tesgi-advisory-os/tesgi/orchestration/contracts.py:71`.
- `STAGE_SCHEMAS` are defined but not referenced elsewhere: `tesgi-advisory-os/tesgi/orchestration/contracts.py:117`.
- Impact: enforcement works today via `cmd_validate`, but contracts are not the single complete source of truth.

6. Claudvisor project instruction document is stale vs current architecture.
- Still references `scripts/validate_kernel.py`, which does not exist in current tree: `TESGI_Claudvisor/TESGI_Advisory_Project_Instructions.md:52`, `TESGI_Claudvisor/TESGI_Advisory_Project_Instructions.md:154`.
- Shows outdated output conventions (`memo.pdf`) vs current workflow (`memo.md` + TESGI packaging pipeline): `TESGI_Claudvisor/TESGI_Advisory_Project_Instructions.md:70`.
- Impact: operator/agent confusion and potential workflow drift.

## Medium

7. Adapter `--force` behavior is overwrite-only and can leave stale files.
- Sync logic copies files/trees but does not prune destination extras: `tesgi-advisory-os/03_tools/adapter/claude_to_tesgi.py:54`, `tesgi-advisory-os/03_tools/adapter/claude_to_tesgi.py:62`, `tesgi-advisory-os/03_tools/adapter/tesgi_to_claude.py:43`, `tesgi-advisory-os/03_tools/adapter/tesgi_to_claude.py:51`.
- Impact: non-round-tripped artifacts can persist and mislead subsequent gates/review.

8. Runtime/work product hygiene is weak in `tesgi-advisory-os`.
- `.gitignore` only contains Python artifacts; run/client outputs are not excluded: `tesgi-advisory-os/.gitignore`.
- Impact: accidental churn in run artifacts and noisy diffs.

9. Spec structure and implementation structure are diverged in tools layout.
- Spec expects dedicated `03_tools/validators/` and `03_tools/packagers/`: `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md:170`.
- Current implementation centralizes gates/packaging in CLI module (`tesgi/__main__.py`) and lacks those directories.
- Impact: harder modular testing and weaker boundary between orchestration vs validators vs packagers.

## Low

10. Custom YAML parser is intentionally minimal and brittle for future policy complexity.
- Parser is line-based and does not support nested YAML semantics: `tesgi-advisory-os/tesgi/__main__.py:81`.
- Impact: low now (current rules are simple), but future policy richness may silently break parsing assumptions.

## Strengths Confirmed

- Core governance gates are active and deterministic (`O/A/B/C/D/E`): `tesgi-advisory-os/tesgi/__main__.py:587`.
- Negative-case regression design is in place and passing: `tesgi-advisory-os/04_evals/regression_suite.yml`.
- Plugin loading is allowlisted and version-pinned: `tesgi-advisory-os/tesgi/plugins/manager.py:41`, `tesgi-advisory-os/00_governance/PLUGIN_ALLOWLIST.json`.
- Cross-workspace mapping includes ESG + sources synchronization: `tesgi-advisory-os/03_tools/adapter/MAPPING_SPEC.md`.

## Amendment Plan (Proposed)

## Phase 0: Governance Consistency (1 day)

1. Add `ADR_0001_Governed_Self_Improvement.md` from template with explicit acceptance record.
2. Align `CHANGE_CONTROL.md` tier taxonomy to spec wording (or update spec with ADR if intentionally changed).
3. Update `TESGI_Claudvisor/TESGI_Advisory_Project_Instructions.md` to current command and artifact flow.

Acceptance:

- ADR file exists and is referenced from governance index.
- Tier definitions no longer conflict between spec and governance.
- Claudvisor instruction doc has no dead script references.

## Phase 1: Command + Packaging Parity (2-3 days)

1. Add CLI commands:
   - `tesgi build-memo <slug>`
   - `tesgi package <slug>`
2. Refactor `tesgi run <slug>` into explicit chain: validate -> build-memo -> package.
3. Expand packaging to include required outputs (or spec-aligned alternative with ADR):
   - `memo.pdf`
   - `invoice.pdf`
   - `receipt.pdf`
   - `runlog.jsonl` (or pointer)
4. Add run artifact pointer for session traceability:
   - `codex_session_pointer.txt` (or approved equivalent)

Acceptance:

- `python -m tesgi --help` lists all spec-required commands.
- Gate D validates generated deliverables and tool/version metadata.
- Run directory contains required pointers and integrity artifacts.

## Phase 2: Gate and Orchestration Deepening (3-4 days)

1. Upgrade Gate A semantic checks to enforce explicit sections for:
   - observations
   - uncertainties
   - risk notes
2. Make stage contracts fully gate-consistent with system policy (`all gates` where required).
3. Enforce `STAGE_SCHEMAS` at runtime during stage evaluation.
4. Add orchestration tests that assert stage/gate coherence.

Acceptance:

- Weak-content kernel fixtures fail Gate A deterministically.
- Contract-required gate sets match documented governance policy.
- Schema violations are surfaced in gate/orchestration outputs.

## Phase 3: Adapter and Repository Hygiene (1-2 days)

1. Add adapter mode for deterministic destination pruning (`--sync-delete`) with guardrails.
2. Add round-trip tests for `claude_to_tesgi.py` <-> `tesgi_to_claude.py`.
3. Update `.gitignore` for run/client runtime outputs per repo policy.

Acceptance:

- Round-trip tests prove no stale artifact drift in managed paths.
- Normal validate/eval/run cycles no longer create noisy untracked churn.

## Phase 4: Structural Alignment (Optional, 2-3 days)

1. Split validator logic from `tesgi/__main__.py` into `03_tools/validators/` and import from CLI.
2. Split packaging logic into `03_tools/packagers/`.
3. Keep CLI as orchestrator only.

Acceptance:

- Validator and packager modules are individually testable.
- CLI remains backward-compatible while architecture matches declared structure.

## Priority Backlog

1. `P0`: Add ADR_0001 + align change tiers + refresh Claudvisor project instructions.
2. `P1`: Implement `build-memo`/`package` command parity + deliverable packaging parity.
3. `P1`: Tighten Gate A semantics.
4. `P2`: Align orchestration contracts to all-gates semantics + enforce stage schemas.
5. `P2`: Add adapter prune mode and round-trip tests.
6. `P3`: Modularize validators/packagers paths to spec structure.

## Recommended Next Action

Start with **Phase 0 + Phase 1** in one controlled amendment branch and require full re-run of:

- `python -m tesgi validate demo`
- `python -m tesgi eval --include-negative`
- `python -m tesgi run demo`

Then update:

- `Governance/TESGI_CANONICAL_SKILL_BUNDLE_v1.0.lock.json`
- `Coordination_Inbox/codex_claude_changelog.md`
