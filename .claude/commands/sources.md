---
name: sources
description: Track source provenance and generate evidence manifest for a client
arguments:
  - name: client-id
    description: The client identifier
    required: true
flags:
  - name: audit
    description: Generate detailed audit report of evidence gaps
    default: false
---

# /project:sources — Source Provenance Tracking

Track, classify, and map all evidence sources supporting the advisory analysis.

## Prerequisites

- Client workspace exists: `clients/[client-id]/`
- Client documents gathered in: `clients/[client-id]/sources/`

## Execution Steps

### 1. Load Client Context

```
Read: clients/$arguments.client-id/intake.md
List: clients/$arguments.client-id/sources/
```

Identify:
- Client-provided documents
- Referenced external sources
- Claims requiring evidence

### 2. Invoke Evidence Notary Skill

```
Load: skills/evidence-notary/SKILL.md
```

### 3. Source Inventory

For each document in `sources/`:

```
Source Inventory Protocol
├── Identify document type
├── Determine provider/author
├── Record date obtained and date of information
├── Classify tier (1-4)
│   ├── Tier 1: Authoritative primary (government, professional reports)
│   ├── Tier 2: Professional secondary (valuations, inspections)
│   ├── Tier 3: Informal (vendor/agent, third-party)
│   └── Tier 4: Unverified/missing
├── Extract claims supported
├── Note reliability factors
└── Assign source ID (SRC-XXX)
```

Reference: `skills/evidence-notary/references/source-types.md`

### 4. Claim-Evidence Mapping

For claims from intake and anticipated analysis:

```
Claim Mapping Protocol
├── Identify factual claims (explicit and implicit)
├── Link each claim to supporting source(s)
├── Assess evidence strength
│   ├── Fully supported (Tier 1-2, current, relevant)
│   ├── Partially supported (some evidence, gaps exist)
│   ├── Weakly supported (Tier 3-4 only)
│   └── Unsupported (no evidence)
└── Flag for uncertainty inventory
```

Reference: `skills/evidence-notary/references/uncertainty-mapping.md`

### 5. Uncertainty Inventory

Compile evidence gaps:

```
Uncertainty Categories
├── Missing sources (assessments not conducted)
├── Stale sources (information may be outdated)
├── Conflicting sources (sources disagree)
├── Low-tier sources (claims rely on weak evidence)
└── Unverifiable claims (cannot be confirmed)
```

Classify impact:
- **Critical:** Could fundamentally change decision
- **Material:** Significantly affects value/risk
- **Minor:** Limited decision impact

### 6. Generate Sources Manifest

Create: `clients/[client-id]/sources/sources_manifest.json`

```json
{
  "case_id": "[client-id]",
  "generated_at": "[timestamp]",
  "generated_by": "TESGI Advisory - Evidence Notary",
  "sources": [
    {
      "id": "SRC-001",
      "type": "[document_type]",
      "tier": 1,
      "description": "[description]",
      "provider": "[provider]",
      "date_obtained": "[date]",
      "date_of_document": "[date]",
      "file_reference": "[path]",
      "claims_supported": ["[claim1]", "[claim2]"],
      "reliability_notes": "[notes]"
    }
  ],
  "uncertainty_map": [
    {
      "claim_id": "CLM-001",
      "claim_text": "[claim]",
      "evidence_status": "[status]",
      "supporting_sources": ["SRC-XXX"],
      "evidence_strength": "[strength]",
      "uncertainty_type": "[type]",
      "uncertainty_impact": "[impact]",
      "gaps": ["[gap1]"],
      "notes": "[notes]"
    }
  ],
  "missing_sources": [
    {
      "type": "[source_type]",
      "why_needed": "[reason]",
      "impact_if_missing": "[impact]",
      "recommended_action": "[action]"
    }
  ],
  "summary": {
    "total_sources": 0,
    "tier_1_count": 0,
    "tier_2_count": 0,
    "tier_3_count": 0,
    "tier_4_count": 0,
    "critical_gaps": 0,
    "material_gaps": 0,
    "evidence_quality": "[high/medium/low/insufficient]"
  }
}
```

### 7. Generate Notes Summary

Create: `clients/[client-id]/sources/notes.md`

```markdown
# Source Provenance Summary

## Evidence Inventory

| ID | Type | Tier | Provider | Claims Supported |
|----|------|------|----------|------------------|
| SRC-001 | ... | ... | ... | ... |

## Evidence Gaps

### Critical Gaps
- [List critical missing sources]

### Material Gaps
- [List material missing sources]

## Recommendations

1. [Recommended action for gap 1]
2. [Recommended action for gap 2]

## Evidence Quality Assessment

Overall: [High/Medium/Low/Insufficient]

[Narrative assessment of evidence sufficiency for decision-making]
```

### 8. Output Summary

Report to user:
- Total sources catalogued
- Evidence quality rating
- Critical gaps requiring action
- Recommended next steps

## Integration with Analysis Workflow

```
/project:intake → /project:sources → /project:esg → /project:analyze → /project:memo
                        │                                    │
                        └────────────────────────────────────┘
                        Sources manifest informs TRUE assessment
```

## Audit Mode (--audit)

When `--audit` flag is set, generate additional:

- Detailed claim-by-claim evidence trace
- Source reliability assessment for each document
- Gap impact analysis
- Recommended due diligence actions with cost/time estimates

## Governance Constraints

Per `artifacts/bridge.md`:
- Uncertainty must be preserved where it exists
- No claims without traceable evidence basis
- Missing evidence must be explicitly disclosed
- Source quality affects decision confidence

## Usage

```bash
# Standard source tracking
/project:sources [client-id]

# With detailed audit report
/project:sources [client-id] --audit
```

## Example

```bash
/project:sources chen-2024-001
```

This catalogues all sources in `clients/chen-2024-001/sources/`, generates `sources_manifest.json`, and creates `notes.md` summary.
