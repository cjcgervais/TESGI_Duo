# ADR 0001: Governed Self-Improvement

## Status
Accepted

## Date
2026-02-06

## Context
TESGI requires an explicit constitutional baseline for self-improving agent behavior. The implementation already uses gates, orchestration contracts, and plugin allowlisting, but this baseline must be materially recorded so change authority is explicit and auditable.

## Decision
1. TESGI changes are controlled by tiered governance and gate enforcement.
2. Constitution-level changes (kernel semantics, role boundaries, scope expansion, command surface changes) are Tier C and require ADR plus explicit human acceptance.
3. A package is authorized only when all core gates pass (`O`, `A`, `B`, `C`, `D`, `E`).
4. Governance and runtime docs must stay in parity with implemented command and packaging behavior.

## Consequences
- Governance drift is easier to detect and reject.
- Higher review burden for constitutional changes is intentional.
- Runtime and documentation updates must be coordinated in one change set when command/gate behavior changes.

## Acceptance Record
Accepted by human operator on 2026-02-06 as part of the full governance/orchestration amendment plan (Phase 0 through Phase 4).
