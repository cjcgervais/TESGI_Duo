---
name: analyze
description: Run TRUE/NORTH/ALIGNED kernel analysis for a client
arguments:
  - name: client-id
    description: The client identifier to analyze
    required: true
flags:
  - name: ultrathink
    description: Enable multi-agent Advisory Council analysis
    default: true
---

# /project:analyze — Decision Kernel Analysis

Run the canonical TRUE/NORTH/ALIGNED decision kernel analysis for a client.

## Prerequisites

- Client intake must be complete: `clients/[client-id]/intake.md`
- Engagement terms confirmed

## Execution Steps

1. **Load Client Context**
   ```
   Read: clients/$arguments.client-id/intake.md
   ```

2. **Invoke Decision Kernel Skill**
   ```
   Load: skills/decision-kernel/SKILL.md
   ```

3. **Execute Advisory Council** (when --ultrathink enabled)

   Invoke specialized subagents in sequence:

   ### Truth Auditor
   - Load: skills/decision-kernel/references/true-assessment.md
   - Validate information integrity
   - Output: clients/[client-id]/analysis/true.md

   ### Horizon Analyst
   - Load: skills/decision-kernel/references/north-assessment.md
   - Assess long-term context
   - Output: clients/[client-id]/analysis/north.md

   ### Coherence Evaluator
   - Load: skills/decision-kernel/references/aligned-assessment.md
   - Test objective-constraint alignment
   - Output: clients/[client-id]/analysis/aligned.md

   ### Synthesis Lead
   - Integrate all findings
   - Determine decision state
   - Prepare for memo generation

4. **Determine Decision State**

   | Condition | State |
   |-----------|-------|
   | All legs pass | **Proceed** |
   | Recoverable gaps | **Pause** |
   | Fundamental issues | **Avoid** |

5. **Output Analysis Summary**
   - Report each leg's status
   - State decision recommendation
   - Note key findings and risks

## Governance Constraints

Per artifacts/bridge.md:
- No outcome guarantees or predictions
- Uncertainty preserved where it exists
- "Walk away" is valid outcome
- Never reframe to force a pass

## Usage

```bash
/project:analyze [client-id] --ultrathink
```

## Example

```bash
/project:analyze smith-2024-001 --ultrathink
```

This runs full Advisory Council analysis with all four subagents.
