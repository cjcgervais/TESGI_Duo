# TRUE Assessment Reference

## Core Question

**Are material facts verifiable, available, and clearly bounded?**

## Assessment Criteria

### 1. Source Verification

| Check | Pass Condition | Fail Condition |
|-------|----------------|----------------|
| Primary sources identified | Direct documentation available | Relying on hearsay or assumptions |
| Source credibility | Official records, registered documents | Unverified claims, promotional material |
| Recency | Information current and valid | Outdated or superseded data |
| Independence | Multiple independent sources corroborate | Single-source dependency |

### 2. Fact Availability

| Check | Pass Condition | Fail Condition |
|-------|----------------|----------------|
| Key documents accessible | Title, zoning, permits obtainable | Critical documents unavailable |
| Public record verification | Can confirm via official channels | No verification pathway |
| Completeness | Material facts substantially covered | Significant gaps in coverage |

### 3. Boundary Clarity

| Check | Pass Condition | Fail Condition |
|-------|----------------|----------------|
| Scope definition | Clear what is/isn't included | Ambiguous boundaries |
| Limitation acknowledgment | Gaps explicitly stated | Hidden assumptions |
| Uncertainty markers | Unknowns labeled as such | False certainty presented |

### 4. Uncertainty Inventory

Document all identified uncertainties:

- **Known unknowns** — Gaps we're aware of
- **Verification blockers** — Facts we cannot confirm
- **Time-sensitive elements** — Information that may change
- **Dependency assumptions** — Facts relying on other facts

## Failure Modes

The TRUE leg fails when:

1. Material facts cannot be independently verified
2. Critical information is unavailable or inaccessible
3. Boundaries are unclear or intentionally obscured
4. Uncertainties are hidden rather than documented
5. Analysis relies on promotional claims rather than verifiable data

## Source Citation Integration

TRUE assessment must integrate with the Evidence Notary skill (`/project:sources`).

### Citing Sources

Reference the sources manifest when making factual claims:

```markdown
## Observations

- Title is clear with no encumbrances [SRC-001: Title Search]
- Zoning permits residential development [SRC-002: Planning Certificate]
- Soil conditions are suitable [SRC-005: Geotechnical Report]
- Contamination status is unknown [NO SOURCE: Gap - Phase 1 ESA not conducted]
```

### Evidence Quality in TRUE

| Evidence State | TRUE Impact |
|----------------|-------------|
| All critical claims Tier 1-2 supported | PASS likely |
| Critical claims have material gaps | FAIL or UNCERTAIN |
| Critical claims unsupported | FAIL |
| Non-critical gaps only | PASS with caveats |

### Required References

Before completing TRUE assessment, ensure:

1. `sources_manifest.json` exists (run `/project:sources` first)
2. All factual claims cite source IDs
3. Uncertainty map is reviewed
4. Missing sources are disclosed

## Output Format

```
TRUE ASSESSMENT
---------------
Status: PASS | PAUSE | FAIL

Evidence Quality: [High/Medium/Low/Insufficient]
Sources Reviewed: [count] (Tier 1: X, Tier 2: Y, Tier 3: Z)

Source Verification:
- [findings with source citations]

Fact Availability:
- [findings with source citations]

Boundary Clarity:
- [findings]

Uncertainty Inventory:
- [list of uncertainties with evidence gap references]

Critical Evidence Gaps:
- [gaps from sources_manifest.json that affect this assessment]

Conclusion:
[Summary statement with specific evidence citations]
```

## Governance Note

Per bridge.md: "Uncertainty is preserved where it exists." Never minimize or dismiss uncertainties to achieve a passing assessment.

Per evidence-notary: All claims must be traceable to sources. Missing evidence must be explicitly disclosed.
