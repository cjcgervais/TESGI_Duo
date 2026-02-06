# Uncertainty Mapping Reference

## Purpose

This reference provides methodology for mapping claims to evidence quality and identifying uncertainty in advisory analysis. Proper uncertainty mapping ensures that decision-makers understand the confidence level of each factual assertion.

## Uncertainty Categories

### 1. Evidential Uncertainty

Uncertainty arising from the quality or availability of evidence.

| Type | Description | Example |
|------|-------------|---------|
| Missing evidence | Required information not obtained | No soil test conducted |
| Weak evidence | Low-tier sources only | Relies on vendor statement alone |
| Conflicting evidence | Sources disagree | Two valuations differ significantly |
| Stale evidence | Information may be outdated | Title search is 6 months old |
| Incomplete evidence | Partial information only | Inspection covered accessible areas only |

### 2. Interpretive Uncertainty

Uncertainty arising from ambiguity in how evidence should be interpreted.

| Type | Description | Example |
|------|-------------|---------|
| Ambiguous language | Document unclear | Covenant wording is vague |
| Professional judgment | Experts may differ | Planners disagree on approval prospects |
| Precedent uncertainty | No clear precedent | Novel planning application |
| Regulatory uncertainty | Rules may change | Policy under review |

### 3. Future Uncertainty

Uncertainty arising from inherently unpredictable future events.

| Type | Description | Example |
|------|-------------|---------|
| Market uncertainty | Future values unknown | Property prices may change |
| Regulatory change | Future rules unknown | Zoning may be reviewed |
| Construction variation | Actual costs may differ | Builder's quote is estimate |
| Timeline uncertainty | Durations may vary | Approval timeline is estimate |

## Uncertainty Impact Levels

### Critical Uncertainty

Uncertainty that could fundamentally change the decision.

**Indicators:**
- Relates to core buildability/usability
- Could result in total loss
- Cannot be bounded without more information
- Affects whether transaction should proceed at all

**Examples:**
- Unknown contamination on industrial site
- Unverified access rights
- Disputed title
- Unknown heritage constraints

**Required Action:** Pause until resolved or Avoid if unresolvable

### Material Uncertainty

Uncertainty that significantly affects value or risk assessment.

**Indicators:**
- Affects cost/value by more than 10%
- Creates ongoing liability exposure
- Requires specific mitigation
- Should be factored into pricing

**Examples:**
- Remediation cost range ($100K-$300K)
- Approval timeline uncertainty (6-18 months)
- Construction cost contingency
- Insurance premium uncertainty

**Required Action:** Disclose explicitly, factor into analysis

### Minor Uncertainty

Uncertainty that exists but has limited decision impact.

**Indicators:**
- Normal transaction uncertainty
- Bounded within acceptable range
- Standard contingencies apply
- Does not change recommendation

**Examples:**
- Exact settlement date
- Minor repair costs
- Normal rate variations
- Standard process timeframes

**Required Action:** Note in analysis, no special treatment

## Claim-Evidence Mapping

### Mapping Process

For each factual claim in the analysis:

```
1. Identify the claim
   └── What specific assertion is being made?

2. Identify supporting evidence
   └── What sources support this claim?
   └── What is the tier of each source?

3. Assess evidence strength
   └── Fully supported: Tier 1-2, current, directly relevant
   └── Partially supported: Some evidence, gaps exist
   └── Weakly supported: Tier 3-4 only
   └── Unsupported: No evidence

4. Classify uncertainty
   └── Type: Evidential / Interpretive / Future
   └── Impact: Critical / Material / Minor

5. Document in uncertainty map
   └── Claim text
   └── Evidence status
   └── Supporting source IDs
   └── Gaps identified
   └── Impact on decision
```

### Evidence Strength Matrix

| Evidence Configuration | Strength Rating | Confidence |
|------------------------|-----------------|------------|
| Multiple Tier 1 sources, consistent | Very Strong | High |
| Single Tier 1 source, current | Strong | High |
| Tier 1 + Tier 2, consistent | Strong | High |
| Tier 2 sources only | Moderate | Medium |
| Tier 2 + Tier 3, consistent | Moderate | Medium |
| Tier 3 sources only | Weak | Low |
| Single Tier 3 source | Very Weak | Low |
| No sources / Tier 4 | None | Cannot assess |

## Uncertainty Map Format

```json
{
  "uncertainty_map": [
    {
      "claim_id": "CLM-001",
      "claim_text": "Property has legal access from public road",
      "evidence_status": "fully_supported",
      "supporting_sources": ["SRC-001", "SRC-005"],
      "evidence_strength": "strong",
      "uncertainty_type": null,
      "uncertainty_impact": null,
      "gaps": [],
      "notes": "Title and survey both confirm access"
    },
    {
      "claim_id": "CLM-002",
      "claim_text": "Site is suitable for residential construction",
      "evidence_status": "partially_supported",
      "supporting_sources": ["SRC-002"],
      "evidence_strength": "moderate",
      "uncertainty_type": "evidential",
      "uncertainty_impact": "critical",
      "gaps": [
        "No geotechnical report - soil conditions unknown",
        "No BAL assessment - bushfire risk unquantified"
      ],
      "notes": "Zoning permits residential but buildability unconfirmed"
    },
    {
      "claim_id": "CLM-003",
      "claim_text": "Property value is approximately $500,000",
      "evidence_status": "weakly_supported",
      "supporting_sources": ["SRC-008"],
      "evidence_strength": "weak",
      "uncertainty_type": "evidential",
      "uncertainty_impact": "material",
      "gaps": [
        "No independent valuation - relies on agent estimate only"
      ],
      "notes": "Agent has financial interest in sale proceeding"
    }
  ]
}
```

## Integration with TRUE Assessment

### Uncertainty Disclosure in TRUE

The TRUE assessment must explicitly address:

1. **Evidence inventory** — What sources were reviewed?
2. **Evidence gaps** — What sources are missing?
3. **Source quality** — What tier are key sources?
4. **Uncertainty impact** — How do gaps affect conclusions?

### TRUE Status Based on Evidence

| Evidence State | TRUE Status |
|----------------|-------------|
| All critical claims strongly supported | PASS |
| Critical claims have material gaps | FAIL or UNCERTAIN |
| Critical claims unsupported | FAIL |
| Non-critical gaps only | PASS with caveats |

### Citation Format

In TRUE/NORTH/ALIGNED documents:

```markdown
## Observations

- Title is clear with no encumbrances [SRC-001: Title Search]
- Zoning permits residential development [SRC-002: Planning Certificate]
- Soil conditions are suitable for construction [NO SOURCE: Gap - soil test not conducted]

## Uncertainties

- **CRITICAL:** Buildability cannot be confirmed without geotechnical assessment
  - Evidence gap: No soil test [Tier 4 - Missing]
  - Impact: Cannot verify foundation requirements or costs
  - Recommended action: Commission geotechnical report before proceeding
```

## Uncertainty Reduction Strategies

### For Evidential Uncertainty

| Strategy | When to Use |
|----------|-------------|
| Commission assessment | Missing professional report |
| Request documents | Documents exist but not provided |
| Independent verification | Vendor claims need confirmation |
| Site inspection | Physical conditions unclear |

### For Interpretive Uncertainty

| Strategy | When to Use |
|----------|-------------|
| Seek professional advice | Legal/planning ambiguity |
| Council pre-application | Planning approval uncertainty |
| Request written confirmation | Verbal advice needs documenting |

### For Future Uncertainty

| Strategy | When to Use |
|----------|-------------|
| Apply contingency | Cost/timeline estimates |
| Conditional approach | Approval-dependent transactions |
| Scenario analysis | Multiple possible outcomes |
| Accept and disclose | Inherently unpredictable matters |
