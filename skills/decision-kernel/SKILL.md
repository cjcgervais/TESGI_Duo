---
name: decision-kernel
description: Applies the TRUE/NORTH/ALIGNED decision kernel to client analysis
version: 1.0.0
triggers:
  - analyze
  - kernel
  - decision analysis
inputs:
  - client-id: The client identifier for the analysis
outputs:
  - Kernel assessment with pass/fail for each leg
  - Decision state recommendation (Proceed/Pause/Avoid)
governance: artifacts/bridge.md
---

# Decision Kernel Skill

## Purpose

This skill applies the canonical TESGI Advisory decision kernel to evaluate whether a client's proposed action should **Proceed**, **Pause**, or be **Avoided**.

## Kernel Structure

All advisory reasoning must pass **all three legs**:

| Leg | Question | Failure Mode |
|-----|----------|--------------|
| **TRUE** | Are material facts verifiable, available, and clearly bounded? | Information integrity compromised |
| **NORTH** | Does the decision make sense over time given known constraints? | Long-term context ignored |
| **ALIGNED** | Do objectives, assumptions, and structure fit together? | Internal coherence broken |

**Critical Rule:** Failure of any leg requires Pause or Avoid. Never reframe to force a pass.

## Execution Protocol

### 1. Invoke Advisory Council

For complex analysis, invoke specialized subagents:

1. **Truth Auditor** — Validates information integrity (TRUE leg)
2. **Horizon Analyst** — Assesses long-term context (NORTH leg)
3. **Coherence Evaluator** — Tests objective-constraint alignment (ALIGNED leg)
4. **Synthesis Lead** — Integrates findings, determines final state

### 2. Assessment Sequence

```
TRUE Assessment
├── Source verification
├── Fact availability check
├── Boundary clarity test
└── Uncertainty inventory

NORTH Assessment
├── Regulatory context review
├── Environmental/hazard exposure
├── Infrastructure constraints
└── Timeline viability

ALIGNED Assessment
├── Objective-constraint mapping
├── Assumption validity test
├── Structural coherence check
└── Risk-goal fit analysis
```

### 3. Decision State Determination

| Condition | State |
|-----------|-------|
| All three legs pass | **Proceed** (with documented caveats) |
| One or more legs fail with recoverable gaps | **Pause** (specify conditions) |
| Fundamental misalignment or unresolvable gaps | **Avoid** |

## Reference Files

- `references/true-assessment.md` — TRUE leg evaluation criteria
- `references/north-assessment.md` — NORTH leg evaluation criteria
- `references/aligned-assessment.md` — ALIGNED leg evaluation criteria

## Governance Constraints

Per `artifacts/bridge.md`:

- No outcome guarantees or predictions
- Uncertainty must be preserved where it exists
- "Walk away" is a valid outcome
- Silent drift is prohibited

## Usage

```bash
/project:analyze [client-id] --ultrathink
```

This skill should be invoked with `ultrathink` for multi-agent kernel analysis.
