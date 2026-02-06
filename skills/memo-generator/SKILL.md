---
name: memo-generator
description: Generates TESGI Advisory Decision Memos from completed kernel analysis
version: 1.0.0
triggers:
  - memo
  - generate memo
  - decision memo
inputs:
  - client-id: The client identifier
  - kernel-analysis: Completed TRUE/NORTH/ALIGNED assessment
outputs:
  - Decision Memo (markdown)
  - Decision state (Proceed/Pause/Avoid)
governance: artifacts/bridge.md
template: assets/memo-template.md
---

# Memo Generator Skill

## Purpose

This skill transforms completed kernel analysis into a client-ready Decision Memo that clearly communicates findings, assessment, and decision state.

## Prerequisites

Before generating a memo:

1. Client intake must be complete (`clients/[client-id]/intake.md`)
2. Kernel analysis must be complete (`clients/[client-id]/analysis/`)
3. All three kernel legs must have documented assessments

## Memo Structure

The Decision Memo follows the template at `assets/memo-template.md`:

1. **Header** — Client, date, service type
2. **Client Objective** — Restated in client's own words
3. **Information Snapshot** — Known facts and uncertainties
4. **TRUE Assessment** — Information integrity findings
5. **NORTH Assessment** — Long-term context findings
6. **ALIGNED Assessment** — Coherence findings
7. **Decision State** — Proceed / Pause / Avoid
8. **Rationale Summary** — Key reasons supporting the state
9. **Limitations** — What the memo does not say

## Language Translation Protocol

### Internal → External Translation

| Internal Language | External Language |
|-------------------|-------------------|
| "Kernel leg fails" | "This area requires additional consideration" |
| "Risk exposure elevated" | "There are factors that may warrant caution" |
| "Information integrity compromised" | "Some information could not be independently verified" |
| "Fundamental misalignment" | "The stated objectives may not align with current constraints" |
| "Avoid recommended" | "Proceeding may not be advisable at this time" |

### Tone Requirements

- **Calm** — No urgency or pressure
- **Plain** — Accessible to non-specialists
- **Non-promotional** — No selling or persuasion
- **Bounded** — Clear about what is and isn't covered

## Decision State Criteria

### Proceed
Use when all three kernel legs pass with only minor caveats.

**Language:** "Conditions appear reasonably satisfied to move forward with caution and awareness."

### Pause
Use when one or more legs have recoverable gaps or require additional information.

**Language:** "Additional information, clarification, or changed assumptions are required before proceeding responsibly."

Must specify:
- What information or clarification is needed
- What conditions would allow re-assessment

### Avoid / Walk Away
Use when fundamental misalignment exists or gaps are unresolvable.

**Language:** "Proceeding would likely rely on unresolved uncertainty, misalignment, or assumptions that cannot be responsibly supported."

## Output Protocol

1. Generate memo using template structure
2. Save to `clients/[client-id]/memo.md`
3. Confirm decision state in summary
4. Note any follow-up clarification allowance (per service terms)

## Governance Constraints

Per `artifacts/bridge.md`:

- No guarantees or predictions
- No outcome advocacy
- Preserve uncertainty where it exists
- Client retains full decision authority
- "Walk away" is a valid outcome

## Usage

```bash
/project:memo [client-id]
```

This skill requires completed kernel analysis before execution.
