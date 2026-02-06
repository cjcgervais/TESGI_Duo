---
name: evidence-notary
description: Tracks source provenance, evidence quality, and uncertainty mapping for advisory decisions
version: 1.0.0
triggers:
  - sources
  - evidence
  - provenance
  - citations
inputs:
  - client-id: The client identifier
  - sources: Documents, reports, and data supporting the analysis
outputs:
  - sources_manifest.json with provenance metadata
  - Uncertainty map linking claims to evidence quality
  - Citation index for TRUE/NORTH/ALIGNED assessments
governance: artifacts/bridge.md
---

# Evidence Notary Skill

## Purpose

This skill tracks the provenance, quality, and reliability of all evidence used in advisory decisions. It creates an auditable chain from claims made in analysis to their underlying sources, enabling transparent uncertainty assessment.

## Why Source Provenance Matters

TESGI Advisory operates on the principle that **correct understanding is the objective**. This requires:

1. **Traceability** — Every factual claim should trace to a source
2. **Quality Assessment** — Not all sources are equally reliable
3. **Uncertainty Mapping** — Gaps in evidence should be explicitly flagged
4. **Audit Trail** — Decisions can be reviewed against their evidence base

## Source Classification

### Tier 1: Authoritative Primary Sources

| Source Type | Examples | Reliability |
|-------------|----------|-------------|
| Government registers | Land titles, EPA registers, planning certificates | High |
| Professional reports | Surveyor reports, BAL assessments, soil tests | High |
| Legal documents | Contracts, vendor statements, caveats | High |
| Official records | Council records, court judgments | High |

### Tier 2: Professional Secondary Sources

| Source Type | Examples | Reliability |
|-------------|----------|-------------|
| Professional assessments | Building inspections, valuations | Medium-High |
| Industry data | Sales comparables, market reports | Medium-High |
| Expert opinions | Legal advice, planning advice | Medium-High |

### Tier 3: Informal Sources

| Source Type | Examples | Reliability |
|-------------|----------|-------------|
| Vendor disclosures | Agent statements, seller claims | Low-Medium |
| Third-party information | Neighbor reports, online data | Low |
| Client assumptions | Unverified client beliefs | Low |

### Tier 4: Unverified / Missing

| Source Type | Examples | Reliability |
|-------------|----------|-------------|
| Assumed facts | "Probably fine", "should be okay" | Very Low |
| Missing data | Assessments not conducted | Unknown |

## Sources Manifest Schema

Create `clients/[client-id]/sources/sources_manifest.json`:

```json
{
  "case_id": "client-id",
  "generated_at": "ISO-8601 timestamp",
  "sources": [
    {
      "id": "SRC-001",
      "type": "title_search",
      "tier": 1,
      "description": "Certificate of Title",
      "provider": "NSW Land Registry Services",
      "date_obtained": "2024-03-15",
      "date_of_document": "2024-03-15",
      "file_reference": "sources/title_search.pdf",
      "claims_supported": [
        "Property is freehold title",
        "No registered encumbrances",
        "Owner is John Smith"
      ],
      "reliability_notes": "Current as of search date",
      "expiry_considerations": "Title may change after search date"
    }
  ],
  "uncertainty_map": [
    {
      "claim": "Site is suitable for residential development",
      "evidence_status": "partially_supported",
      "supporting_sources": ["SRC-001", "SRC-003"],
      "gaps": ["No soil test conducted", "BAL assessment pending"],
      "impact_on_decision": "Cannot confirm buildability without missing assessments"
    }
  ],
  "missing_sources": [
    {
      "type": "soil_test",
      "why_needed": "Required to confirm foundation requirements",
      "impact_if_missing": "Cannot verify buildability",
      "recommended_action": "Commission geotechnical assessment"
    }
  ]
}
```

## Execution Protocol

### 1. Source Inventory

For each document/source provided or referenced:

```
Source Inventory
├── Identify source
│   ├── Document type
│   ├── Provider/author
│   ├── Date obtained
│   └── Date of information
├── Classify tier (1-4)
├── Extract claims supported
├── Note reliability factors
└── Assign source ID (SRC-XXX)
```

### 2. Claim Mapping

For each factual claim in TRUE/NORTH/ALIGNED analysis:

```
Claim Mapping
├── Identify claim
├── Link to supporting source(s)
├── Assess evidence strength
│   ├── Fully supported (Tier 1-2 source, current, relevant)
│   ├── Partially supported (Some evidence, gaps exist)
│   ├── Weakly supported (Tier 3-4 only)
│   └── Unsupported (No evidence, assumption only)
└── Flag for uncertainty inventory
```

### 3. Uncertainty Inventory

Compile all evidence gaps:

```
Uncertainty Inventory
├── Missing sources (assessments not conducted)
├── Stale sources (information may be outdated)
├── Conflicting sources (sources disagree)
├── Low-tier sources (claims rely on weak evidence)
└── Unverifiable claims (cannot be confirmed)
```

### 4. Generate Manifest

Create `sources_manifest.json` with:
- Complete source inventory
- Claim-to-source mapping
- Uncertainty map
- Missing source recommendations

## Integration with Decision Kernel

### TRUE Leg Integration

The Evidence Notary directly feeds TRUE assessment:

| Evidence Status | TRUE Impact |
|-----------------|-------------|
| All claims Tier 1-2 supported | TRUE likely PASS |
| Critical claims unsupported | TRUE likely FAIL |
| Mixed evidence quality | TRUE requires explicit uncertainty disclosure |

### Citation Format in Analysis

When writing TRUE/NORTH/ALIGNED assessments, cite sources:

```markdown
## Observations

- Property title is clear with no encumbrances [SRC-001]
- Zoning permits residential use [SRC-002]
- Soil conditions are unknown [NO SOURCE - gap identified]
```

## Output Files

1. **sources_manifest.json** — Machine-readable source inventory
2. **sources/notes.md** — Human-readable source summary
3. **Citation annotations** — Source IDs in analysis files

## Reference Files

- `references/source-types.md` — Detailed source classification guide
- `references/uncertainty-mapping.md` — Uncertainty assessment methodology

## Governance Constraints

Per `artifacts/bridge.md`:

- Uncertainty must be preserved where it exists
- No claims without traceable evidence basis
- Missing evidence must be explicitly disclosed
- Source quality affects decision confidence

## Usage

```bash
/project:sources [client-id]
```

Run after gathering client documents and before `/project:analyze`.
