# Environmental Assessment Reference

## Purpose

This reference guides environmental risk evaluation for land acquisition decisions. Environmental factors often carry long-tail liability and can render land unbuildable or economically unviable.

## Assessment Categories

### 1. Climate Risk Exposure

#### Flood
| Check | Data Source | Risk Indicator |
|-------|-------------|----------------|
| Flood zone classification | Local council flood maps, state flood databases | Zone 1-3 designation |
| Historical flood events | Council records, insurance claims data | Frequency and severity |
| Flood overlay on title | Planning certificate, Section 32/149 | Overlay present |
| Stormwater infrastructure | Council drainage plans | Capacity constraints |

**Red Flags:**
- Property in 1-in-100 year flood zone without mitigation
- No flood study available for waterway-adjacent land
- Insurance exclusions for flood damage

#### Bushfire
| Check | Data Source | Risk Indicator |
|-------|-------------|----------------|
| Bushfire Attack Level (BAL) | BAL assessment report, CFA/RFS maps | BAL-12.5 to BAL-FZ |
| Bushfire Management Overlay | Planning certificate | BMO present |
| Defendable space requirements | BAL assessment | Setback mandates |
| Construction cost impact | Builder quotes at BAL rating | Cost premium % |

**Red Flags:**
- BAL-40 or BAL-FZ without client awareness of build cost
- Insufficient land for required defendable space
- Access road not compliant with emergency vehicle requirements

#### Other Climate
| Check | Data Source | Risk Indicator |
|-------|-------------|----------------|
| Sea level rise projection | Coastal hazard mapping | Inundation timeline |
| Drought / water scarcity | Catchment authority data | Allocation reliability |
| Extreme heat exposure | Climate projections | Infrastructure stress |

### 2. Contamination

#### Historical Land Use
| Previous Use | Contamination Risk | Assessment Required |
|--------------|-------------------|---------------------|
| Industrial / manufacturing | High | Phase 1 + Phase 2 ESA |
| Fuel storage / service station | High | Phase 1 + Phase 2 ESA |
| Agricultural (intensive) | Medium | Soil testing |
| Orchards / vineyards | Medium | Pesticide residue testing |
| Landfill / waste disposal | Very High | Full contamination audit |
| Residential | Low | Visual inspection |
| Greenfield | Low | Desktop review |

#### Assessment Hierarchy
1. **Desktop review** — Historical aerial photos, title history, EPA records
2. **Phase 1 ESA** — Site inspection, interviews, records review
3. **Phase 2 ESA** — Soil and groundwater sampling
4. **Remediation Action Plan** — If contamination confirmed

**Red Flags:**
- Seller resistance to contamination assessment
- EPA notice on title
- Adjacent industrial or waste sites
- Unknown fill material on site

### 3. Ecological Constraints

#### Protected Matters
| Matter | Governing Framework | Consequence |
|--------|---------------------|-------------|
| Threatened species | EPBC Act (federal), state biodiversity acts | Referral required, offset obligations |
| Endangered ecological communities | EPBC Act, state planning | Development restrictions |
| Wetlands (RAMSAR) | EPBC Act | Buffer requirements |
| Migratory species | EPBC Act | Seasonal constraints |

#### Vegetation
| Check | Data Source | Risk Indicator |
|-------|-------------|----------------|
| Native vegetation overlay | Planning certificate | Clearing restrictions |
| Tree protection orders | Council registers | Removal permits required |
| Riparian buffers | Waterway authority | Setback from waterways |
| Significant trees | Arborist assessment | Protected specimens |

**Red Flags:**
- Critically endangered ecological community on site
- Koala habitat or similar high-profile species
- Remnant vegetation covering buildable area
- Wetland or waterway through site

### 4. Resources and Rights

#### Water
| Check | Data Source | Risk Indicator |
|-------|-------------|----------------|
| Water license / allocation | State water authority | Volume and reliability |
| Bore permits | State water authority | Extraction limits |
| Riparian rights | Title, water authority | Access restrictions |
| Tank water viability | Rainfall data, roof catchment | Self-sufficiency |

#### Other Resources
| Check | Data Source | Risk Indicator |
|-------|-------------|----------------|
| Mineral rights | Title search | Severed rights |
| Petroleum / gas exploration | State resources department | Active licenses |
| Carbon credits | Carbon registry | Encumbered land |
| Biodiversity offsets | State biodiversity registers | Offset obligations |

## Output Template

```markdown
## Environmental Assessment

### Climate Risk
**Flood:** [Low/Medium/High/Unknown]
- Zone classification: [X]
- Overlay status: [Yes/No]
- Key finding: [Summary]

**Bushfire:** [Low/Medium/High/Unknown]
- BAL rating: [X]
- Overlay status: [Yes/No]
- Key finding: [Summary]

**Other climate:** [Low/Medium/High/Unknown]
- Key finding: [Summary]

### Contamination
**Risk Level:** [Low/Medium/High/Unknown]
- Historical use: [Description]
- Assessment completed: [None/Phase 1/Phase 2]
- Key finding: [Summary]

### Ecological
**Risk Level:** [Low/Medium/High/Unknown]
- Protected matters: [Yes/No/Unknown]
- Vegetation constraints: [Description]
- Key finding: [Summary]

### Resources
**Water security:** [Adequate/Marginal/Inadequate/Unknown]
- Key finding: [Summary]

### Environmental Summary
| Factor | Rating | Kernel Impact |
|--------|--------|---------------|
| Flood | | TRUE: / NORTH: |
| Bushfire | | TRUE: / NORTH: |
| Contamination | | TRUE: / NORTH: |
| Ecological | | TRUE: / ALIGNED: |
| Water | | NORTH: |
```

## Uncertainty Handling

When environmental data is unavailable:
1. State explicitly what is unknown
2. Estimate cost and time to obtain information
3. Flag whether gap is material to decision
4. Recommend Pause if gap affects buildability or liability
