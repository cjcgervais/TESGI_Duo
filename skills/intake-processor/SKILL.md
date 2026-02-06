---
name: intake-processor
description: Processes client intake forms and prepares analysis workspace
version: 1.0.0
triggers:
  - intake
  - new client
  - process intake
inputs:
  - client-id: Unique identifier for the client
  - intake-form: Completed intake form data
outputs:
  - Validated intake record
  - Client workspace structure
  - Analysis readiness confirmation
governance: artifacts/bridge.md
reference-form: artifacts/intake-form.md
---

# Intake Processor Skill

## Purpose

This skill processes client intake submissions, validates completeness, creates the client workspace, and confirms readiness for kernel analysis.

## Intake Processing Protocol

### 1. Receive Intake

Accept intake data in any of these formats:
- Completed intake form (markdown or PDF)
- Structured data matching intake form fields
- Email/message with required information

### 2. Validate Completeness

Check for required fields per `artifacts/intake-form.md`:

| Field | Required | Validation |
|-------|----------|------------|
| Client name/identifier | Yes | Non-empty |
| Contact information | Yes | Valid format |
| Property/decision description | Yes | Sufficient detail for analysis |
| Client's stated objective | Yes | Clear, specific |
| Timeline/urgency factors | Yes | Documented |
| Known constraints | Yes | Listed or "none identified" |
| Budget/resource context | Optional | If relevant to decision |
| Prior analysis/advice received | Optional | For context |

### 3. Create Client Workspace

```
clients/[client-id]/
├── intake.md           # Validated intake record
├── analysis/           # Kernel analysis workspace
│   ├── true.md         # TRUE assessment
│   ├── north.md        # NORTH assessment
│   └── aligned.md      # ALIGNED assessment
├── sources/            # Reference documents
└── memo.md             # Final decision memo (generated)
```

### 4. Confirm Engagement Terms

Before proceeding, verify:
- [ ] Client has received `artifacts/overview.md`
- [ ] Scope confirmed per `artifacts/pricing.md`
- [ ] Payment received (if applicable)
- [ ] Client understands advisory-only nature

## Validation Rules

### Information Sufficiency

The intake must provide enough information to:
1. Understand what decision the client faces
2. Identify what property/land/development is involved
3. Know what outcome the client hopes to achieve
4. Recognize any time constraints or pressures

### Red Flags at Intake

Flag for attention if:
- Client expects transaction support (out of scope)
- Client seeks validation rather than analysis
- Urgency suggests pressure-driven decision
- Objective is vague or shifts during intake
- Client dismisses need for constraints discussion

### Intake Validation Output

```
INTAKE VALIDATION
-----------------
Client ID: [client-id]
Status: COMPLETE | INCOMPLETE | FLAGGED

Required Fields:
- [field]: [status]

Completeness: [X/Y fields complete]

Flags:
- [any red flags identified]

Readiness: READY FOR ANALYSIS | NEEDS CLARIFICATION

Next Steps:
- [specific actions needed]
```

## Reference Files

- `references/intake-validation.md` — Detailed validation criteria
- `artifacts/intake-form.md` — Standard intake form template
- `artifacts/overview.md` — Client overview document
- `artifacts/pricing.md` — Engagement and pricing terms

## Governance Constraints

Per `artifacts/bridge.md`:

- Advisory only — no representation implied
- Scope must be explicitly confirmed
- Client retains decision authority
- Boundaries reinforced at intake

## Usage

```bash
/project:intake [client-id]
```

This skill should be run before any kernel analysis begins.
