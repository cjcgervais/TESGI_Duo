# CHANGE CONTROL

Changes are classified by tier. Agents propose; gates decide; humans merge.

## Tier A (Safe Auto-Propose)
- Internal scripts/tooling
- Eval expansion and packaging reliability
- Dependency updates with pinned versions
- Merge still requires passing gates and human signoff

## Tier B (Client Trust Surface)
- Handout wording
- Memo template language
- Pricing/engagement and invoice/receipt language
- Requires explicit client-surface diff summary plus human approval

## Tier C (Constitution-Level)
- Kernel definitions (`TRUE` / `NORTH` / `ALIGNED`)
- Role boundary rules and scope expansion
- Command/gate semantics that change service meaning
- Requires ADR + explicit risk note + explicit human acceptance

## Governance ADRs
- ADR index: `00_governance/ADR/README.md`
- Bootstrap baseline: `00_governance/ADR/ADR_0001_Governed_Self_Improvement.md`
