# TASK: Semantic Gate Validation & Negative Test Suite

**Status:** NOT STARTED
**Assigned:** Codex 5.3
**Fallback:** Claude Opus 4.5
**Created:** 2026-02-06
**Priority:** CRITICAL

---

## Objective

Transform TESGI gates from structural checks to semantic validators, and create a robust negative test suite to prove they work.

---

## Progress Tracker

Mark items `[x]` when complete. If session ends mid-task, note current state in "Handoff Notes" section.

### Phase 1: Gate B Semantic Validation
- [ ] 1.1 Add `parse_decision_state()` helper to extract Proceed/Pause/Avoid from memo
- [ ] 1.2 Add `section_has_list_items(content, section_name)` helper
- [ ] 1.3 Add `section_has_content(content, section_name)` helper
- [ ] 1.4 Add `kernel_has_blockers(base_dir)` to scan `02_analysis/*.md` for FAIL/unbounded markers
- [ ] 1.5 Update `gate_decision_state()` to enforce:
  - [ ] Exactly ONE decision state marked
  - [ ] Pause requires non-empty "Missing Information List" with ≥1 item
  - [ ] Avoid requires non-empty "Rationale Summary" with content
  - [ ] Proceed blocked if kernel files contain blockers
- [ ] 1.6 Test with existing golden cases (should still pass)

### Phase 2: Gate A Semantic Validation
- [ ] 2.1 Add `validate_kernel_content(filepath, required_sections)` helper
- [ ] 2.2 Define required sections per file:
  - [ ] `true.md`: Source Verification, Fact Availability, Boundary Clarity, Status line
  - [ ] `north.md`: Regulatory/Planning, Timeline/Horizon, Status line
  - [ ] `aligned.md`: Objectives, Constraints/Assumptions, Status line
- [ ] 2.3 Update `gate_kernel()` to validate content not just existence
- [ ] 2.4 Test with existing golden cases (should still pass)

### Phase 3: Gate E - Sources Manifest (New Core Gate)
- [ ] 3.1 Add `gate_sources(base_dir)` function
- [ ] 3.2 Validation rules:
  - [ ] `01_sources/sources_manifest.json` must exist
  - [ ] Must have ≥1 source entry
  - [ ] Each entry must have: id, type, tier, description
- [ ] 3.3 Update `run_gates()` to include Gate E
- [ ] 3.4 Update gate output display to show E gate
- [ ] 3.5 Test with existing golden cases (will fail until cases updated)

### Phase 4: Update Existing Golden Cases
- [ ] 4.1 Add `01_sources/sources_manifest.json` to CASE_0001
- [ ] 4.2 Add `01_sources/sources_manifest.json` to CASE_0002
- [ ] 4.3 Add `01_sources/sources_manifest.json` to CASE_0003
- [ ] 4.4 Add `01_sources/sources_manifest.json` to CASE_0004
- [ ] 4.5 Add `01_sources/sources_manifest.json` to CASE_0005
- [ ] 4.6 Add `01_sources/sources_manifest.json` to CASE_0006
- [ ] 4.7 Verify all kernel files have required sections (add if missing)
- [ ] 4.8 Run `python -m tesgi eval` — all 6 cases must PASS

### Phase 5: Negative Test Suite
- [ ] 5.1 Create `04_evals/golden_cases/FAIL_B_001/` — No decision state marked
- [ ] 5.2 Create `04_evals/golden_cases/FAIL_B_002/` — Pause without Missing Information List
- [ ] 5.3 Create `04_evals/golden_cases/FAIL_B_003/` — Avoid without Rationale Summary
- [ ] 5.4 Create `04_evals/golden_cases/FAIL_B_004/` — Proceed with TRUE leg FAIL status
- [ ] 5.5 Create `04_evals/golden_cases/FAIL_A_001/` — true.md missing required section
- [ ] 5.6 Create `04_evals/golden_cases/FAIL_A_002/` — north.md missing Status line
- [ ] 5.7 Create `04_evals/golden_cases/FAIL_E_001/` — sources_manifest.json missing
- [ ] 5.8 Create `04_evals/golden_cases/FAIL_E_002/` — sources_manifest.json empty/invalid

### Phase 6: Expected-Fail Support in Eval
- [ ] 6.1 Update `04_evals/regression_suite.yml` schema to support:
  ```yaml
  cases:
    - path: 04_evals/golden_cases/CASE_0001
    - path: 04_evals/golden_cases/FAIL_B_001
      expect: fail
      gate: B
  ```
- [ ] 6.2 Update `cmd_eval()` to parse expected outcomes
- [ ] 6.3 Add `--include-negative` flag to eval command
- [ ] 6.4 Update eval reporting to show "(expected)" for anticipated failures
- [ ] 6.5 Final test: `python -m tesgi eval --include-negative` passes with 8 expected failures

### Phase 7: Final Validation & Commit
- [ ] 7.1 Run full test suite: `python -m tesgi eval`
- [ ] 7.2 Run with negative cases: `python -m tesgi eval --include-negative`
- [ ] 7.3 Verify no regressions in `python -m tesgi validate demo`
- [ ] 7.4 Commit all changes with descriptive message
- [ ] 7.5 Log completion in `Coordination_Inbox/codex_claude_changelog.md`

---

## Technical Specifications

### Gate B Decision State Rules

```python
# Pseudo-code for gate_decision_state() enhancement

def gate_decision_state(base_dir):
    memo = read_memo(base_dir)

    # 1. Extract decision state
    state = parse_decision_state(memo)  # Returns: "Proceed" | "Pause" | "Avoid" | None | "Multiple"

    if state is None:
        return FAIL("No decision state marked")
    if state == "Multiple":
        return FAIL("Multiple decision states marked - exactly one required")

    # 2. State-specific rules
    if state == "Pause":
        if not section_has_list_items(memo, "Missing Information List"):
            return FAIL("Pause requires non-empty Missing Information List")

    if state == "Avoid":
        if not section_has_content(memo, "Rationale Summary"):
            return FAIL("Avoid requires Rationale Summary with content")

    if state == "Proceed":
        blockers = kernel_has_blockers(base_dir)
        if blockers:
            return FAIL(f"Proceed blocked by kernel issues: {blockers}")

    return PASS(f"Decision state valid: {state}")
```

### Kernel Blocker Patterns

Scan `02_analysis/true.md`, `north.md`, `aligned.md` for:

```python
BLOCKER_PATTERNS = [
    r"Status:\s*FAIL",
    r"(?i)unbounded\s+uncertainty",
    r"(?i)cannot\s+be\s+verified",
    r"(?i)missing\s+required",
    r"(?i)fundamental\s+misalignment",
    r"(?i)critical\s+gap",
]
```

### Gate A Required Sections

```python
KERNEL_REQUIREMENTS = {
    "true.md": {
        "sections": ["Source Verification", "Fact Availability", "Boundary Clarity"],
        "alt_sections": ["Sources", "Facts", "Boundaries"],  # Acceptable alternatives
        "require_status": True,
    },
    "north.md": {
        "sections": ["Regulatory", "Timeline"],
        "alt_sections": ["Planning", "Horizon", "Context"],
        "require_status": True,
    },
    "aligned.md": {
        "sections": ["Objectives", "Constraints"],
        "alt_sections": ["Assumptions", "Structure"],
        "require_status": True,
    },
}
```

### Sources Manifest Schema

```json
{
  "sources": [
    {
      "id": "SRC-001",           // Required
      "type": "title_search",    // Required
      "tier": 1,                 // Required: 1-4
      "description": "...",      // Required
      "provider": "...",         // Optional
      "date_obtained": "...",    // Optional
      "claims_supported": []     // Optional
    }
  ]
}
```

### Negative Case Minimal Structure

Each FAIL_* case needs minimal files to reach the target gate:

```
FAIL_B_001/
├── 00_intake/
│   └── intake.md (minimal)
├── 02_analysis/
│   ├── true.md (valid, PASS)
│   ├── north.md (valid, PASS)
│   └── aligned.md (valid, PASS)
├── 03_memo/
│   └── Decision_Memo.md (NO decision state marked) ← triggers Gate B fail
├── 04_package/
│   ├── manifest.json
│   └── gate_report.json
└── 01_sources/
    └── sources_manifest.json (valid)
```

---

## File Locations

| Purpose | Path |
|---------|------|
| Main CLI | `tesgi-advisory-os/tesgi/__main__.py` |
| Orchestration | `tesgi-advisory-os/tesgi/orchestration/` |
| Plugins | `tesgi-advisory-os/tesgi/plugins/` |
| Governance | `tesgi-advisory-os/00_governance/` |
| Golden cases | `tesgi-advisory-os/04_evals/golden_cases/` |
| Regression suite | `tesgi-advisory-os/04_evals/regression_suite.yml` |
| Changelog | `Coordination_Inbox/codex_claude_changelog.md` |

---

## Acceptance Criteria

```bash
# All positive cases pass with new gates
python -m tesgi eval
# Expected: EVAL: PASS (6 cases)
# Gates shown: O, A, B, C, D, E

# All negative cases fail on expected gate
python -m tesgi eval --include-negative
# Expected: EVAL: PASS (14 cases, 8 expected failures)
# Each FAIL_* case shows "(expected)" annotation

# Demo still works
python -m tesgi validate demo
# Expected: All gates PASS

# Run packaging still works
python -m tesgi run demo
# Expected: Creates run artifact in runs/
```

---

## Handoff Notes

**Last completed phase:** (update when handing off)

**Current work in progress:** (describe partially complete work)

**Blockers or issues encountered:** (note any problems)

**Files modified so far:** (list files touched)

**Tests run:** (note what's been validated)

---

## Commit Message Template

```
Implement semantic gate validation and negative test suite

Gate B enhancements:
- Validate exactly one decision state marked
- Pause requires Missing Information List with items
- Avoid requires Rationale Summary with content
- Proceed blocked by kernel FAIL/unbounded uncertainty markers

Gate A enhancements:
- Validate kernel files have required sections
- Check for Status lines in true/north/aligned assessments

Gate E (new):
- Require sources_manifest.json with valid entries
- Promoted from optional plugin to core gate

Test suite:
- Added 8 negative test cases (FAIL_B_001 through FAIL_E_002)
- Added --include-negative flag to eval command
- Updated regression_suite.yml with expect annotations
- Updated CASE_0001-0006 with sources_manifest.json

All tests pass: 6 positive cases, 8 expected failures.
```

---

## Reference Documents

- Kernel rules: `tesgi-advisory-os/00_governance/KERNEL.md`
- Boundaries: `tesgi-advisory-os/00_governance/BOUNDARIES.md`
- Language rules: `tesgi-advisory-os/00_governance/LANGUAGE_RULES.yml`
- Evidence Notary skill: `TESGI_Claudvisor/skills/evidence-notary/SKILL.md`
- Decision Kernel skill: `TESGI_Claudvisor/skills/decision-kernel/SKILL.md`
- Audit report: `Coordination_Inbox/codex_claude_changelog.md` (2026-02-06 entry)
