# TESGI Advisory

Non-representational decision analysis for land, property, and development decisions.

## Decision Kernel (Apply to Every Analysis)

| Leg | Must Pass |
|-----|-----------|
| **TRUE** | Facts verifiable, available, clearly bounded |
| **NORTH** | Decision sensible over time given constraints |
| **ALIGNED** | Objectives, assumptions, structure fit together |

Failure of any leg → **Pause** or **Avoid**. Never reframe to force a pass.

## Boundaries (Hard Constraints)

- Advisory only — no representation, brokerage, or agency
- No guarantees, predictions, or outcome promises
- Client retains full decision authority
- "Walk away" is a valid outcome

## Commands

```bash
/project:intake [client-id]    # Process intake form
/project:esg [client-id]       # Run ESG impact assessment
/project:analyze [client-id]   # Run kernel analysis (use --ultrathink)
/project:memo [client-id]      # Generate decision memo
```

## Project Structure

```
├── .claude/commands/       # Slash command definitions
├── artifacts/              # Core documents (bridge, overview, pricing)
├── skills/
│   ├── decision-kernel/    # TRUE/NORTH/ALIGNED analysis
│   ├── esg-analyst/        # ESG impact assessment
│   ├── memo-generator/     # Decision memo production
│   └── intake-processor/   # Client intake validation
├── clients/                # Active client work (gitignored)
└── outputs/                # Final deliverables
```

## Skills

| Skill | Purpose | Trigger |
|-------|---------|---------|
| `decision-kernel` | Apply TRUE/NORTH/ALIGNED analysis | `/project:analyze` |
| `esg-analyst` | ESG impact assessment for land acquisition | `/project:esg` |
| `memo-generator` | Generate client Decision Memo | `/project:memo` |
| `intake-processor` | Validate and setup client workspace | `/project:intake` |

## Advisory Council (Subagent Pattern)

For complex analysis, invoke specialized subagents:
1. **Truth Auditor** — Information integrity (TRUE leg)
2. **Horizon Analyst** — Long-term context (NORTH leg)
3. **Coherence Evaluator** — Objective-constraint alignment (ALIGNED leg)
4. **Synthesis Lead** — Final determination

Use `ultrathink` for multi-agent kernel analysis.

## Language Rules

- **Internal:** Precise, analytical ("kernel leg fails", "risk elevated")
- **External:** Calm, plain, non-promotional ("further information needed")
- Never use urgency, certainty, or persuasion with clients

## Governance

See `artifacts/bridge.md` for authoritative constraints.
Silent drift is prohibited. Document all scope changes.
