# TESGI Duo Advisory Audit: Claude Opus 4.5 + Codex 5.3 Combined Assessment

## Executive Summary

I've audited the codebase including the Codex V2 Orchestration Report. The foundation is **strong** — clear governance intent, well-defined boundaries, and a canonical decision kernel (TRUE/NORTH/ALIGNED). However, there are significant implementation gaps and architectural opportunities for the Duo Advisory model.

---

## Part 1: Validation of Codex V2 Findings

The Codex report identified 8 issues. My assessment:

| Finding | Codex Severity | Claude Assessment | Notes |
|---------|----------------|-------------------|-------|
| Gate behavior doesn't match spec | Critical | **Confirmed Critical** | CLI gates check file existence, not semantic content |
| Dual workspace bypass | Critical | **Confirmed Critical** | `02_client_work/<slug>` vs `clients/<client-id>` divergence |
| Language rule disclaimer conflict | High | **Confirmed High** | "represent" banned but disclaimer requires "non-representational" |
| Thin regression suite | High | **Confirmed High** | Golden case has placeholder content that passes gates |
| CLI/spec command mismatch | High | **Medium** | Existing commands work, just need `build-memo` and `package` |
| Missing validator script | Medium | **Low** | Documented but not blocking |
| Skill metadata alignment | Medium | **Low** | Claude commands work despite frontmatter differences |
| Change control tier drift | Medium | **Medium** | Tier labels A/B/C reversed from spec |

---

## Part 2: Additional Findings (Claude Audit)

### Critical Gap: No ESG Analysis Framework
The current system handles general land acquisition decisions but lacks explicit ESG (Environmental, Social, Governance) assessment structures required for a proper ESG advisory service.

**Missing components:**
- No environmental impact assessment template
- No social impact evaluation criteria
- No governance risk scoring
- No ESG-specific vocabulary in `LANGUAGE_RULES.yml`

### High: Decision State Validation Is Shallow
`tesgi/__main__.py:205-222` — Gate B only checks for section headers, not:
- Whether exactly ONE decision state is marked
- Rule-specific requirements (Proceed/Pause/Avoid conditions from spec)
- Presence of Missing Information List for Pause
- Presence of Rationale Summary for Avoid

### High: No Source Provenance Tracking
The spec mentions `sources_manifest.json` but:
- No validation that sources are cited
- No uncertainty mapping to source quality
- No chain-of-custody for evidence

### Medium: Claude Skill Architecture Underutilized
The Claude commands (`/project:analyze`, `/project:intake`, `/project:memo`) are well-designed but:
- No integration with canonical CLI gates
- No shared state between Claude and CLI workflows
- Advisory Council subagent pattern exists but isn't formalized

---

## Part 3: Duo Advisory Architecture Recommendations

### The Core Insight
Claude Opus 4.5 and Codex 5.3 have complementary strengths:

| Capability | Claude Opus 4.5 | Codex 5.3 |
|------------|-----------------|-----------|
| Extended reasoning | `ultrathink` multi-agent analysis | Focused code generation |
| Code execution | Limited (sandbox) | Full environment access |
| Iterative refinement | Strong context retention | Session-based execution |
| Architectural planning | Holistic system design | Task-oriented planning |
| Real-time interaction | Conversational advisory | Batch processing |

### Proposed 2-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TESGI DUO ADVISORY                           │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1: ADVISORY INTELLIGENCE (Claude Opus 4.5)              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  /project:intake   → Intake Sentinel                     │  │
│  │  /project:analyze  → Advisory Council (ultrathink)       │  │
│  │       ├── Truth Auditor (TRUE leg)                       │  │
│  │       ├── Horizon Analyst (NORTH leg)                    │  │
│  │       ├── Coherence Evaluator (ALIGNED leg)              │  │
│  │       └── Synthesis Lead (decision state)                │  │
│  │  /project:memo     → Memo Assembler                      │  │
│  │  /project:esg      → ESG Impact Analyst (NEW)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓ Artifacts                          │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: EXECUTION & GOVERNANCE (Codex 5.3)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Adapters                                                 │  │
│  │       ├── claude_to_tesgi.py (workspace sync)            │  │
│  │       └── tesgi_to_claude.py (state export)              │  │
│  │  Orchestration Engine                                     │  │
│  │       ├── State machine (9 stages)                       │  │
│  │       └── Stage contracts (JSON Schema)                  │  │
│  │  Validators (Gates A-E)                                   │  │
│  │       ├── gate_a_kernel.py (semantic checks)             │  │
│  │       ├── gate_b_decision_state.py (rule validation)     │  │
│  │       ├── gate_c_boundary_lint.py (token-aware)          │  │
│  │       ├── gate_d_package_integrity.py (hash + PDF)       │  │
│  │       └── gate_e_regression.py (golden case suite)       │  │
│  │  Packagers                                                │  │
│  │       └── PDF generation, manifest, run logs             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 4: ESG Advisory Enhancement

For land acquisition ESG advisory, add these specialized components:

### ESG Decision Kernel Extension

```yaml
# Add to KERNEL.md
## ESG OVERLAY
All land acquisition advice must also satisfy:

### Environmental (E)
- Ecological impact bounded and disclosed
- Climate risk exposure assessed
- Contamination/remediation status known

### Social (S)
- Community impact considered
- Indigenous/heritage constraints verified
- Access and displacement implications stated

### Governance (G)
- Regulatory compliance pathway clear
- Ownership structure transparent
- Conflict of interest disclosed
```

### New ESG Analysis Template

```markdown
# ESG Impact Assessment

## Environmental Factors
- [ ] Flood zone classification
- [ ] Bushfire Attack Level (BAL)
- [ ] Contamination history
- [ ] Protected species/habitat
- [ ] Water rights/catchment

## Social Factors
- [ ] Cultural heritage sites
- [ ] Native title claims
- [ ] Community impact
- [ ] Infrastructure access

## Governance Factors
- [ ] Zoning compliance
- [ ] Development approval pathway
- [ ] Ownership chain
- [ ] Encumbrances/easements

## ESG Risk Score
| Factor | Rating | Evidence |
|--------|--------|----------|
| E      |        |          |
| S      |        |          |
| G      |        |          |
```

---

## Part 5: Priority Implementation Roadmap

### Phase 1: Foundation (Critical - Do First)

1. **Fix Language Rule Conflict**
   - Update `LANGUAGE_RULES.yml` to use phrase matching, not substring
   - Add explicit exception for required disclaimer language

2. **Deepen Gate B Validation**
   ```python
   # gate_b_decision_state.py
   - Parse for exactly ONE checked box in Decision State section
   - If Pause: require "Missing Information List" section
   - If Avoid: require "Rationale Summary" section
   - If Proceed: verify no "unbounded uncertainty" in TRUE/NORTH/ALIGNED
   ```

3. **Create Workspace Adapter**
   - Bidirectional sync between `clients/<id>` and `02_client_work/<slug>`
   - Field mapping with validation

### Phase 2: Orchestration (High Priority)

4. **Implement State Machine**
   ```python
   STATES = [
       "intake_ready",
       "true_complete",
       "north_complete",
       "aligned_complete",
       "esg_assessed",        # NEW for ESG
       "decision_synthesized",
       "memo_built",
       "boundary_passed",
       "package_passed",
       "eval_passed"
   ]
   ```

5. **Add ESG Analysis Skill**
   - New skill: `skills/esg-analyst/SKILL.md`
   - New command: `/project:esg [client-id]`
   - Integrate into Advisory Council workflow

### Phase 3: Quality Assurance

6. **Expand Golden Cases**
   - Minimum 10 cases covering:
     - Proceed with clean ESG
     - Pause for missing environmental data
     - Avoid due to social/heritage issues
     - Boundary language violations
     - Package integrity failures

7. **Add Semantic Gate A Checks**
   - Verify TRUE contains explicit uncertainty inventory
   - Verify NORTH contains risk timeline
   - Verify ALIGNED contains objective-constraint mapping

---

## Part 6: Synergy Recommendations

### Claude-Led Workflows
- Client intake conversations (nuanced question handling)
- Advisory Council deliberation (multi-perspective analysis)
- Complex case synthesis (weighing competing factors)
- ESG impact narrative generation

### Codex-Led Workflows
- Gate validation execution
- Package generation (PDF, manifest, hashes)
- Codebase refactoring and tooling improvements
- Regression test execution

### Handoff Protocol
```
1. Claude completes analysis → writes to clients/<id>/
2. Codex adapter syncs to 02_client_work/<slug>/
3. Codex runs full gate suite
4. If PASS: Codex packages deliverables
5. If FAIL: Claude receives gate report for revision
```

---

## Part 7: Immediate Action Items

### Start Here (Ordered by Impact)

| Priority | Task | Owner | Impact |
|----------|------|-------|--------|
| 1 | Fix disclaimer/language rule conflict in `LANGUAGE_RULES.yml` | Codex | Unblocks valid memos |
| 2 | Create `claude_to_tesgi.py` adapter | Codex | Unifies workspaces |
| 3 | Deepen Gate B decision state validation | Codex | Enforces spec compliance |
| 4 | Create ESG analysis skill | Claude | Enables ESG advisory |
| 5 | Add 5+ golden cases with real content | Both | Catches regressions |
| 6 | Implement orchestration state machine | Codex | Enforces stage order |
| 7 | Add source provenance tracking | Claude | Evidence chain |
| 8 | Wire Claude commands to canonical CLI | Both | Full Duo integration |

---

## Conclusion

The Codex V2 report provides an excellent technical roadmap. My additions:

1. **ESG-specific framework** — Essential for a land acquisition ESG advisory service
2. **2-Layer architecture** — Claude for intelligence, Codex for execution
3. **Synergy model** — Clear division of responsibilities
4. **Semantic gate depth** — Move beyond file existence to content validation

The foundation is solid. The spec is thoughtful. The implementation gap is fixable. With these enhancements, TESGI Duo Advisory can deliver on the promise of "magnificent and safe" — invalid states truly unbuildable, with ESG considerations properly integrated into every land acquisition decision.

---

## Appendix: File References

Key files reviewed in this audit:

| File | Purpose |
|------|---------|
| `tesgi-advisory-os/DUO_ADVISORY_ORCHESTRATION_V2_REPORT.md` | Codex orchestration report |
| `tesgi-advisory-os/TESGI_Advisory_Spec_v01.md` | Canonical spec |
| `tesgi-advisory-os/00_governance/KERNEL.md` | Core invariants |
| `tesgi-advisory-os/00_governance/BOUNDARIES.md` | Hard constraints |
| `tesgi-advisory-os/00_governance/LANGUAGE_RULES.yml` | Forbidden/required terms |
| `tesgi-advisory-os/00_governance/CHANGE_CONTROL.md` | Tier definitions |
| `tesgi-advisory-os/tesgi/__main__.py` | CLI implementation |
| `TESGI_Claudvisor/CLAUDE.md` | Claude project config |
| `TESGI_Claudvisor/skills/decision-kernel/SKILL.md` | Kernel analysis skill |
| `TESGI_Claudvisor/.claude/commands/analyze.md` | Analyze command |
| `TESGI_Claudvisor/clients/test-2024-001/memo.md` | Example memo output |

---

**Prepared by:** Claude Opus 4.5
**Companion report:** DUO_ADVISORY_ORCHESTRATION_V2_REPORT.md (Codex 5.3)
**Date:** 2026-02-05
**Mode:** Audit and architecture recommendation
