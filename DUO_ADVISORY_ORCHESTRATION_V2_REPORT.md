# TESGI Duo Advisory: Orchestration V2 Audit and Recommendations

## Next Step: Concrete Orchestration V2 (Start Here)

### Objective
Build a single, governed orchestration layer that works for both Codex and Claude Code Opus 4.5 without drift in structure, policy, or output quality.

### Step 1: Unify the canonical workspace model
- Canonical path: `02_client_work/<slug>/`
- Keep current TESGI CLI as system-of-record for packaging and gate checks.
- Add an adapter that can ingest/export Claude workspace paths (`TESGI_Claudvisor/clients/<client-id>/`) into the canonical model.

Deliverables:
- `03_tools/adapter/claude_to_tesgi.py`
- `03_tools/adapter/tesgi_to_claude.py`
- Mapping spec: field-level and file-level conversion table.

Acceptance criteria:
- Any Claude case can be converted to canonical format and pass structural validation.
- Round-trip conversion does not lose decision state, rationale, or disclaimer sections.

### Step 2: Implement explicit orchestration state machine
Define strict stages and contracts:
1. `intake_ready`
2. `true_complete`
3. `north_complete`
4. `aligned_complete`
5. `decision_synthesized`
6. `memo_built`
7. `boundary_passed`
8. `package_passed`
9. `eval_passed`

Deliverables:
- `03_tools/orchestration/states.py`
- `03_tools/orchestration/engine.py`
- Contract schemas for each stage (JSON Schema or Pydantic models).

Acceptance criteria:
- `north` cannot run before `true`.
- `aligned` cannot run before `north`.
- package step is blocked unless all required gates pass.

### Step 3: Rebuild gates to match TESGI spec behavior
Implement full parity with `TESGI_Advisory_Spec_v01.md`:
- Gate A checks required sections and content semantics (observations, uncertainties, risk notes) in TRUE/NORTH/ALIGNED outputs.
- Gate B validates exactly one decision state and rule-specific requirements:
  - Proceed blocked on unbounded uncertainty.
  - Pause requires explicit missing information list.
  - Avoid requires explicit rationale summary.
- Gate C enforces disclaimer and boundary language with token-aware matching (avoid accidental substring conflicts).
- Gate D checks package integrity including PDF generation and tool version capture.
- Gate E runs mandatory golden regression checks during `tesgi run`.

Deliverables:
- `03_tools/validators/gate_a_kernel.py`
- `03_tools/validators/gate_b_decision_state.py`
- `03_tools/validators/gate_c_boundary_lint.py`
- `03_tools/validators/gate_d_package_integrity.py`
- `03_tools/validators/gate_e_regression.py`

Acceptance criteria:
- `tesgi run <slug>` fails on any gate mismatch.
- Gate reports include deterministic, human-readable failure reasons.

### Step 4: Introduce plugin interfaces for controlled extensibility
Add plugin hooks so improvements do not require kernel rewrites:
- `workflow_plugin`
- `policy_plugin`
- `llm_gateway_plugin`
- `telemetry_plugin`
- `eval_plugin`

Deliverables:
- Plugin contract docs and reference implementations.
- Plugin loading with allowlist and version pinning.

Acceptance criteria:
- Plugins can be enabled/disabled per run.
- Kernel invariants remain enforced regardless of plugin set.

### Step 5: Deploy specialized sub-agents as skills
Deploy and wire these agents into orchestration:
- `intake-sentinel` (intake completeness and scope boundaries)
- `truth-auditor` (TRUE leg)
- `horizon-analyst` (NORTH leg)
- `coherence-evaluator` (ALIGNED leg)
- `decision-synthesizer` (single decision state and synthesis)
- `boundary-guardian` (external language and disclaimer enforcement)
- `evidence-notary` (source provenance and uncertainty map)
- `memo-assembler` (memo generation)
- `package-steward` (manifest/hash/pdf packaging)
- `eval-warden` (golden case regression and drift checks)
- `adr-clerk` (tier detection and change control compliance)

Acceptance criteria:
- Agent outputs are schema-validated.
- Every agent step records run metadata and artifact pointers.

---

## Executive Summary

This codebase has a strong governance intent but current implementation drift allows low-quality or incomplete artifacts to pass gates. The highest-value improvement is to unify orchestration across the two workspace models and enforce full gate parity with the written TESGI spec.

---

## Audit Findings (Prioritized)

### Critical
1. Gate behavior does not match spec depth.
- Spec requires semantic checks for kernel outputs and decision-state rules.
- Current implementation mostly checks file existence/headers and manifest shape.
- References:
  - `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md`
  - `tesgi-advisory-os/tesgi/__main__.py`

2. Dual workspace model can bypass governance consistency.
- CLI model: `02_client_work/<slug>/.../03_memo/Decision_Memo.md`
- Claude command model: `clients/<client-id>/.../memo.md`
- References:
  - `tesgi-advisory-os/tesgi/__main__.py`
  - `TESGI_Claudvisor/.claude/commands/memo.md`

### High
3. Language rule conflict around representational disclaimer.
- Spec requires explicit non-representational disclaimer language.
- Language rules currently ban `represent` and `representation`, while lint uses substring matching.
- References:
  - `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md`
  - `tesgi-advisory-os/00_governance/LANGUAGE_RULES.yml`
  - `tesgi-advisory-os/tesgi/__main__.py`

4. Regression suite is too thin.
- Only one golden case, and placeholder analysis content still passes.
- References:
  - `tesgi-advisory-os/04_evals/regression_suite.yml`
  - `tesgi-advisory-os/04_evals/golden_cases/CASE_0001/02_analysis/true.md`

5. CLI command surface differs from spec.
- Spec lists `build-memo` and `package` commands.
- CLI currently exposes `init-client`, `validate`, `run`, `eval`.
- References:
  - `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md`
  - `tesgi-advisory-os/tesgi/__main__.py`

### Medium
6. Documented validator script is missing.
- `scripts/validate_kernel.py` is referenced but not present.
- References:
  - `TESGI_Claudvisor/TESGI_Advisory_Project_Instructions.md`

7. Skill metadata is not aligned with Codex skill frontmatter guidance.
- Existing `SKILL.md` frontmatter includes additional fields (`version`, `triggers`, `inputs`, `outputs`, etc.).
- Codex skill guidance expects only `name` and `description` in frontmatter.
- References:
  - `TESGI_Claudvisor/skills/*/SKILL.md`
  - `C:/Users/Chad/.codex/skills/.system/skill-creator/SKILL.md`

8. Change-control tier semantics drift from spec framing.
- `CHANGE_CONTROL.md` tier definitions do not match v0.1 spec tier intent.
- References:
  - `tesgi-advisory-os/00_governance/CHANGE_CONTROL.md`
  - `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md`

---

## Plugin Recommendations

### Core stack
1. Workflow orchestration: Temporal or Prefect.
2. Policy enforcement: OPA/Rego (+ Regal linting).
3. LLM routing and fallback: LiteLLM.
4. Observability and tracing: OpenTelemetry + Langfuse.
5. Contract and schema enforcement: Pydantic + JSON Schema.
6. Prompt/eval regression: promptfoo.

### Why this stack
- Durable runs and retries for long advisory workflows.
- Explicit policy engine for non-negotiable boundary rules.
- Provider flexibility without rewriting orchestrator logic.
- Run-level observability for governance and auditability.
- Strict IO contracts between sub-agents.

---

## Specialized Agent Blueprint (TESGI Duo)

| Agent | Skill Focus | Inputs | Outputs | Gate Impact |
|---|---|---|---|---|
| Intake Sentinel | intake validation | intake form, scope terms | intake status, missing info list | A, B |
| Truth Auditor | TRUE analysis | sources, intake | `true.md` with evidence and uncertainties | A |
| Horizon Analyst | NORTH analysis | true findings, context data | `north.md` with long-range constraints | A |
| Coherence Evaluator | ALIGNED analysis | true+north findings, objectives | `aligned.md` with fit assessment | A |
| Decision Synthesizer | decision state | three leg outputs | one valid state + rationale block | B |
| Boundary Guardian | language policy | draft memo | boundary lint report + fixes | C |
| Evidence Notary | provenance | sources and citations | source manifest + uncertainty map | A, D |
| Memo Assembler | memo generation | all prior outputs | `Decision_Memo.md` | B, C |
| Package Steward | packaging | memo + artifacts | pdfs, manifest, gate report | D |
| Eval Warden | regression | golden cases + current output | pass/fail deltas | E |
| ADR Clerk | change control | changed files + tier map | ADR requirement decision + checklist | governance |

---

## Claude Code Opus 4.5 Compatibility Notes

This report is intentionally plain Markdown and command-oriented so it can be consumed directly by Claude Code Opus 4.5 and Codex.

### Command compatibility layer
- Canonical execution: `python -m tesgi <command>`
- Claude slash command wrappers can call canonical CLI commands after adapter conversion.

Suggested wrapper map:
- `/project:intake <client-id>` -> `tesgi init-client <slug>` + intake adapter
- `/project:analyze <client-id>` -> orchestration engine stages `true/north/aligned/synthesis`
- `/project:memo <client-id>` -> `build-memo` stage (new command)
- `/project:package <client-id>` -> `package` stage (new command)
- `/project:run <client-id>` -> canonical `tesgi run <slug>`

### Output conventions for Duo Advisory
- Keep both model-facing and client-facing text separated.
- Preserve uncertainty labels explicitly.
- Require explicit non-representational disclaimer section.
- Keep decision state singular and machine-parseable.

---

## Recommended 14-Day Implementation Plan

1. Days 1-2
- finalize canonical model and adapter spec.
- add conversion scripts and fixture tests.

2. Days 3-5
- implement orchestration state engine with schema contracts.
- enforce stage dependencies.

3. Days 6-8
- rewrite gates A-E to spec parity.
- add richer gate report diagnostics.

4. Days 9-10
- add plugin interfaces and baseline implementations.
- integrate telemetry and policy checks.

5. Days 11-12
- expand golden cases to at least 10 scenarios:
  - proceed, pause, avoid
  - missing-info edge cases
  - language-boundary violations
  - packaging integrity failures

6. Days 13-14
- wire Claude wrappers to canonical CLI.
- complete documentation and ADR updates.
- run full regression before release.

---

## Success Metrics
- New case initialization under 60 seconds.
- 100 percent gate enforcement parity with spec requirements.
- No package built when any gate fails.
- Full traceability from memo to manifest, run record, and tool version metadata.
- Zero silent governance drift across Codex and Claude paths.

---

Prepared for: TESGI Duo Advisory
Date: 2026-02-06
Mode: Audit and architecture recommendation
