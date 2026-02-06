---
name: esg
description: Run ESG (Environmental, Social, Governance) impact assessment for a client
arguments:
  - name: client-id
    description: The client identifier to assess
    required: true
flags:
  - name: dimension
    description: Focus on specific ESG dimension (e, s, g, or all)
    default: all
---

# /project:esg — ESG Impact Assessment

Run Environmental, Social, and Governance impact assessment for land acquisition decisions.

## Prerequisites

- Client intake must be complete: `clients/[client-id]/intake.md`
- Recommended: Run before or alongside `/project:analyze`

## Execution Steps

### 1. Load Client Context

```
Read: clients/$arguments.client-id/intake.md
```

Identify from intake:
- Property location and type
- Client objectives and risk tolerance
- Known constraints and concerns
- Available documentation

### 2. Invoke ESG Analyst Skill

```
Load: skills/esg-analyst/SKILL.md
```

### 3. Execute ESG Assessment

For each dimension (or specified `--dimension`):

#### Environmental Assessment
```
Load: skills/esg-analyst/references/environmental.md
```

Evaluate:
- Climate risk (flood, bushfire, other)
- Contamination (historical use, testing status)
- Ecological constraints (protected matters, vegetation)
- Resource rights (water, minerals, carbon)

Output: Environmental findings with risk rating

#### Social Assessment
```
Load: skills/esg-analyst/references/social.md
```

Evaluate:
- Heritage (Indigenous, non-Indigenous)
- Community impact (character, opposition, infrastructure)
- Access and displacement (occupants, access rights)
- Economic factors (agricultural, employment)

Output: Social findings with risk rating

#### Governance Assessment
```
Load: skills/esg-analyst/references/governance.md
```

Evaluate:
- Title and ownership (chain, encumbrances, disputes)
- Regulatory compliance (zoning, building, environmental)
- Structural factors (entity, financing, exit)
- Disclosure and conflicts

Output: Governance findings with risk rating

### 4. Generate ESG Report

Create: `clients/[client-id]/analysis/esg.md`

Structure:
```markdown
# ESG Impact Assessment

**Client:** [client-id]
**Date:** [assessment date]
**Assessor:** TESGI Advisory (ESG Analyst)

---

## Environmental (E)
**Rating:** [Low/Medium/High/Unknown]

### Findings
[Observations by category]

### Uncertainties
[Information gaps]

### Kernel Integration
- TRUE impact: [fact availability implications]
- NORTH impact: [long-term constraint implications]

---

## Social (S)
**Rating:** [Low/Medium/High/Unknown]

[Same structure]

---

## Governance (G)
**Rating:** [Low/Medium/High/Unknown]

[Same structure]

---

## ESG Summary Table

| Dimension | Rating | Key Risk | Kernel Leg Affected |
|-----------|--------|----------|---------------------|
| E | | | |
| S | | | |
| G | | | |

## Recommendation to Kernel

[How ESG findings should inform Proceed/Pause/Avoid decision]

---

*ESG assessment is advisory only. Ratings reflect available information and identified uncertainties. This assessment does not constitute environmental audit, heritage survey, or legal compliance certification.*
```

### 5. Output Summary

Report to user:
- Overall ESG risk profile
- Critical findings requiring attention
- Information gaps that may require Pause
- Handoff notes for `/project:analyze`

## Integration with Decision Kernel

ESG findings feed directly into TRUE/NORTH/ALIGNED:

| ESG Finding | Kernel Impact |
|-------------|---------------|
| High E risk (unbounded) | TRUE fails — facts not available |
| Unknown contamination | TRUE uncertain — Pause likely |
| Heritage site on property | TRUE + ALIGNED — objective may conflict |
| Community opposition risk | NORTH — long-term context factor |
| Title dispute | TRUE fails — ownership unclear |
| Non-compliant structures | TRUE — material fact |
| Inadequate due diligence time | Governance — timeline pressure risk |

## Governance Constraints

Per `artifacts/bridge.md`:
- No outcome guarantees or predictions
- Uncertainty preserved where it exists
- ESG ratings are advisory, not certification
- "Walk away" is valid when ESG risk is unacceptable
- Never reframe to minimize genuine risk

## Usage

```bash
# Full ESG assessment
/project:esg [client-id]

# Environmental focus only
/project:esg [client-id] --dimension e

# Social focus only
/project:esg [client-id] --dimension s

# Governance focus only
/project:esg [client-id] --dimension g
```

## Example

```bash
/project:esg mitchell-2024-001
```

This runs full ESG assessment and creates `clients/mitchell-2024-001/analysis/esg.md`.
