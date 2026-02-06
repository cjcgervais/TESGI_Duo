# TESGI Canonical Skill Bundle v1.0

Status: LOCKED  
Effective date: 2026-02-06  
Applies to: TESGI Advisory operations (Duo workflow with Codex + Claude)

## Normative Rule

The canonical bundle is exactly the set defined in:

- `Governance/TESGI_CANONICAL_SKILL_BUNDLE_v1.0.lock.json`

Any skill addition, removal, rename, or content change that alters bundle hashes is non-compliant until approved and re-locked.

## Governance Baseline

The bundle is governed by:

- `tesgi-advisory-os/00_governance/KERNEL.md`
- `tesgi-advisory-os/00_governance/BOUNDARIES.md`
- `tesgi-advisory-os/00_governance/LANGUAGE_RULES.yml`
- `tesgi-advisory-os/00_governance/CHANGE_CONTROL.md`
- `tesgi-advisory-os/00_governance/PLUGIN_ALLOWLIST.json`

Required runtime gate baseline:

- `O` Orchestration state order
- `A` Kernel completeness
- `B` Decision state validity
- `C` Language lint
- `D` Packaging integrity
- `E` Sources manifest

## Locked Skill Set

## Claude required skills

- `decision-kernel`
- `intake-processor`
- `evidence-notary`
- `esg-analyst`
- `memo-generator`

## Codex required skills

- `doc`
- `figma-implement-design`
- `gh-address-comments`
- `jupyter-notebook`
- `notion-knowledge-capture`
- `notion-research-documentation`
- `notion-spec-to-implementation`
- `pdf`
- `playwright`
- `screenshot`
- `security-best-practices`
- `security-ownership-map`
- `security-threat-model`
- `spreadsheet`

## Codex system skill baseline

- `skill-installer` is treated as preinstalled system capability.

## Compliance Verification

1. Run:
   - `python -m tesgi validate demo`
   - `python -m tesgi eval --include-negative`
   - `python 03_tools/plugins/list_allowlisted_plugins.py`
2. Verify the skill hashes in:
   - `Governance/TESGI_CANONICAL_SKILL_BUNDLE_v1.0.lock.json`
3. Confirm governance file hashes in the same lock file are unchanged.

## Change Procedure (for v1.1+)

1. Draft RFC/ADR with reason, risk, and impact.
2. Obtain explicit human approval.
3. Apply skill/governance changes.
4. Regenerate lock file hashes.
5. Re-run full validation/eval checks.
6. Record change in `Coordination_Inbox/codex_claude_changelog.md`.

