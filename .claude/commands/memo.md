---
name: memo
description: Generate Decision Memo from completed analysis
arguments:
  - name: client-id
    description: The client identifier for memo generation
    required: true
---

# /project:memo — Decision Memo Generation

Generate a client-ready Decision Memo from completed kernel analysis.

## Prerequisites

- Client intake complete: `clients/[client-id]/intake.md`
- Kernel analysis complete:
  - `clients/[client-id]/analysis/true.md`
  - `clients/[client-id]/analysis/north.md`
  - `clients/[client-id]/analysis/aligned.md`

## Execution Steps

1. **Verify Prerequisites**
   - Check intake exists and is valid
   - Confirm all three kernel assessments complete
   - Verify decision state determined

2. **Load Memo Generator Skill**
   ```
   Load: skills/memo-generator/SKILL.md
   Template: skills/memo-generator/assets/memo-template.md
   ```

3. **Gather Analysis Inputs**
   ```
   Read: clients/$arguments.client-id/intake.md
   Read: clients/$arguments.client-id/analysis/true.md
   Read: clients/$arguments.client-id/analysis/north.md
   Read: clients/$arguments.client-id/analysis/aligned.md
   ```

4. **Apply Language Translation**

   Convert internal analysis language to client-appropriate language:

   | Internal | External |
   |----------|----------|
   | "Kernel leg fails" | "This area requires additional consideration" |
   | "Risk exposure elevated" | "There are factors that may warrant caution" |
   | "Fundamental misalignment" | "Objectives may not align with constraints" |

5. **Generate Decision Memo**

   Following template structure:
   - Client objective (in their words)
   - Information snapshot
   - TRUE assessment findings
   - NORTH assessment findings
   - ALIGNED assessment findings
   - Decision state (Proceed/Pause/Avoid)
   - Rationale summary
   - Limitations statement

6. **Output Memo**
   ```
   Write: clients/$arguments.client-id/memo.md
   ```

7. **Confirm Delivery**
   - Report memo location
   - State decision recommendation
   - Note clarification allowance (if applicable)

## Decision State Language

### Proceed
"Conditions appear reasonably satisfied to move forward with caution and awareness."

### Pause
"Additional information, clarification, or changed assumptions are required before proceeding responsibly."

### Avoid
"Proceeding would likely rely on unresolved uncertainty, misalignment, or assumptions that cannot be responsibly supported."

## Governance Constraints

Per artifacts/bridge.md:
- No guarantees or predictions
- No outcome advocacy
- Calm, plain, non-promotional language
- Client retains decision authority

## Usage

```bash
/project:memo [client-id]
```

## Example

```bash
/project:memo smith-2024-001
```

This generates the Decision Memo at `clients/smith-2024-001/memo.md`.
