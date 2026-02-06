# Intake Validation Reference

## Purpose

This reference provides detailed criteria for validating client intake submissions before proceeding to kernel analysis.

## Required Information Categories

### 1. Client Identification

| Field | Requirement | Validation Criteria |
|-------|-------------|---------------------|
| Name | Required | Full legal name or entity name |
| Contact | Required | Email and/or phone for clarification |
| Client ID | Generated | Unique identifier for workspace |

### 2. Decision Context

| Field | Requirement | Validation Criteria |
|-------|-------------|---------------------|
| Property/Subject | Required | Specific address, parcel, or description |
| Decision type | Required | Purchase, development, hold, exit, etc. |
| Current status | Required | Ownership status, stage of process |
| Geographic context | Required | Municipality, region, jurisdiction |

### 3. Client Objectives

| Field | Requirement | Validation Criteria |
|-------|-------------|---------------------|
| Primary objective | Required | Clear statement of what client wants to achieve |
| Success criteria | Required | How client would define a good outcome |
| Constraints acknowledged | Required | What limits client has identified |
| Risk tolerance | Recommended | Client's stated comfort with uncertainty |

### 4. Timeline & Urgency

| Field | Requirement | Validation Criteria |
|-------|-------------|---------------------|
| Decision timeline | Required | When decision must be made |
| External deadlines | If applicable | Offer expiry, permit windows, etc. |
| Urgency source | Required | Why timeline exists (internal vs external) |

### 5. Prior Work

| Field | Requirement | Validation Criteria |
|-------|-------------|---------------------|
| Prior advice | Recommended | Other professionals consulted |
| Existing reports | If available | Appraisals, inspections, studies |
| Previous attempts | If applicable | Prior offers, applications, etc. |

## Validation Process

### Step 1: Completeness Check

```
For each required field:
  IF field is empty or unclear:
    Mark INCOMPLETE
    Add to clarification list
  ELSE:
    Mark COMPLETE
```

### Step 2: Coherence Check

Verify internal consistency:
- Does objective match decision type?
- Does timeline match decision complexity?
- Do constraints align with stated goals?

### Step 3: Scope Alignment Check

Verify request is within service scope:
- Is this advisory-appropriate? (not transaction support)
- Is the subject matter land/property/development related?
- Can desktop analysis reasonably address the question?

### Step 4: Red Flag Assessment

Check for warning indicators:

| Red Flag | Indicator | Response |
|----------|-----------|----------|
| Scope creep risk | Vague or expanding objectives | Clarify and bound |
| Validation seeking | Client has already decided | Discuss purpose of analysis |
| External pressure | Urgency from third parties | Document and assess |
| Information withholding | Reluctance to share constraints | Address before proceeding |
| Unrealistic expectations | Seeking guarantees or predictions | Reinforce boundaries |

## Validation Output Template

```markdown
# Intake Validation Report

**Client ID:** [client-id]
**Validation Date:** [date]
**Validator:** TESGI Advisory

## Completeness Summary

| Category | Status | Notes |
|----------|--------|-------|
| Client Identification | [Complete/Incomplete] | |
| Decision Context | [Complete/Incomplete] | |
| Client Objectives | [Complete/Incomplete] | |
| Timeline & Urgency | [Complete/Incomplete] | |
| Prior Work | [Complete/N/A] | |

## Overall Status

**Validation Result:** [READY / NEEDS CLARIFICATION / OUT OF SCOPE]

## Clarification Needed

[List any items requiring client clarification]

## Red Flags Identified

[List any warning indicators and recommended handling]

## Engagement Confirmation

- [ ] Client received overview document
- [ ] Scope confirmed
- [ ] Payment received
- [ ] Advisory-only nature understood

## Next Steps

[Specific actions to proceed]
```

## Governance Alignment

Per `artifacts/bridge.md`:

- Intake establishes scope — scope cannot silently expand later
- Advisory-only nature must be clear from the start
- Client decision authority is preserved throughout
- Boundaries are reinforced, not assumed
