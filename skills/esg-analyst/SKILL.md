---
name: esg-analyst
description: Applies ESG (Environmental, Social, Governance) impact assessment to land acquisition decisions
version: 1.0.0
triggers:
  - esg
  - environmental
  - sustainability
  - impact assessment
inputs:
  - client-id: The client identifier for the assessment
outputs:
  - ESG impact assessment with risk ratings per dimension
  - ESG-specific uncertainties and gaps
  - Integration points with TRUE/NORTH/ALIGNED kernel
governance: artifacts/bridge.md
---

# ESG Analyst Skill

## Purpose

This skill applies ESG (Environmental, Social, Governance) impact assessment specifically tailored for land acquisition decisions. It operates as an overlay to the canonical TRUE/NORTH/ALIGNED kernel, adding domain-specific risk identification.

## ESG Framework for Land Acquisition

All land acquisition advisory must evaluate three ESG dimensions:

| Dimension | Core Question | Failure Mode |
|-----------|---------------|--------------|
| **Environmental (E)** | Are ecological, climate, and contamination risks bounded? | Hidden environmental liability |
| **Social (S)** | Are community, heritage, and access impacts understood? | Social license failure |
| **Governance (G)** | Is regulatory pathway and ownership structure clear? | Compliance or title failure |

**Critical Rule:** Unbounded ESG risk in any dimension must inform the kernel decision state. ESG failures typically trigger Pause or Avoid.

## Relationship to Decision Kernel

ESG assessment is not separate from TRUE/NORTH/ALIGNED — it feeds into each leg:

```
ESG Assessment
    │
    ├── Environmental findings → TRUE (fact availability, evidence quality)
    │                         → NORTH (long-term constraints, climate exposure)
    │
    ├── Social findings       → TRUE (heritage verification, access rights)
    │                         → ALIGNED (objective-community fit)
    │
    └── Governance findings   → TRUE (title clarity, encumbrances)
                              → NORTH (regulatory trajectory)
                              → ALIGNED (structure-objective coherence)
```

## Execution Protocol

### 1. Environmental Assessment

Evaluate using `references/environmental.md`:

```
Environmental Factors
├── Climate Risk
│   ├── Flood zone classification
│   ├── Bushfire Attack Level (BAL)
│   ├── Sea level / storm surge exposure
│   └── Drought / water availability
├── Contamination
│   ├── Historical land use
│   ├── Soil / groundwater testing
│   └── Remediation obligations
├── Ecological
│   ├── Protected species / habitat
│   ├── Vegetation clearing restrictions
│   └── Waterway / wetland buffers
└── Resources
    ├── Water rights / allocation
    ├── Mineral / extraction rights
    └── Carbon / biodiversity offsets
```

### 2. Social Assessment

Evaluate using `references/social.md`:

```
Social Factors
├── Heritage
│   ├── Indigenous / First Nations sites
│   ├── Cultural heritage overlays
│   ├── Archaeological sensitivity
│   └── Native title claims
├── Community
│   ├── Neighborhood character
│   ├── Community opposition risk
│   ├── Infrastructure capacity
│   └── Services access (school, health)
├── Access & Displacement
│   ├── Existing occupants / tenants
│   ├── Public access rights
│   ├── Easements affecting use
│   └── Relocation obligations
└── Employment & Economy
    ├── Local employment impact
    ├── Agricultural land preservation
    └── Economic dependency factors
```

### 3. Governance Assessment

Evaluate using `references/governance.md`:

```
Governance Factors
├── Title & Ownership
│   ├── Clear chain of title
│   ├── Encumbrances / caveats
│   ├── Boundary disputes
│   └── Adverse possession claims
├── Regulatory Compliance
│   ├── Zoning conformity
│   ├── Development approval pathway
│   ├── Use restrictions
│   └── Permit requirements
├── Structural
│   ├── Ownership entity suitability
│   ├── Tax implications
│   ├── Financing constraints
│   └── Exit strategy viability
└── Conflicts & Disclosure
    ├── Seller disclosure completeness
    ├── Agent conflicts
    ├── Related party transactions
    └── Advisor independence
```

### 4. ESG Risk Scoring

| Rating | Definition | Kernel Impact |
|--------|------------|---------------|
| **Low** | Risk identified, bounded, manageable | Proceed with documented caveats |
| **Medium** | Risk identified, partially bounded, requires mitigation | Pause likely; specify conditions |
| **High** | Risk unbounded or mitigation unclear | Avoid unless risk accepted explicitly |
| **Unknown** | Insufficient information to assess | Pause; add to Missing Information List |

### 5. Output Format

Generate `clients/[client-id]/analysis/esg.md` with:

```markdown
# ESG Impact Assessment

## Environmental (E)
**Rating:** [Low/Medium/High/Unknown]

### Findings
- [Specific observations]

### Uncertainties
- [What is not known]

### Kernel Integration
- TRUE impact: [How this affects information integrity]
- NORTH impact: [How this affects long-term context]

---

## Social (S)
**Rating:** [Low/Medium/High/Unknown]

[Same structure]

---

## Governance (G)
**Rating:** [Low/Medium/High/Unknown]

[Same structure]

---

## ESG Summary

| Dimension | Rating | Key Risk | Kernel Leg Affected |
|-----------|--------|----------|---------------------|
| E         |        |          |                     |
| S         |        |          |                     |
| G         |        |          |                     |

## Recommendation to Kernel
[How ESG findings should influence the Proceed/Pause/Avoid decision]
```

## Reference Files

- `references/environmental.md` — Environmental assessment criteria and data sources
- `references/social.md` — Social impact evaluation framework
- `references/governance.md` — Governance and compliance checklist

## Governance Constraints

Per `artifacts/bridge.md`:

- No outcome guarantees or predictions
- Uncertainty must be preserved where it exists
- ESG ratings are advisory, not certification
- "Walk away" remains valid when ESG risk is unacceptable
- Silent drift is prohibited

## Usage

```bash
/project:esg [client-id]
```

This skill should be invoked before or alongside `/project:analyze` to ensure ESG factors inform the kernel assessment.
