# TESGI Advisory — Agentic Project

Non-representational decision clarity for land, property, and development decisions.

## Quick Start

```bash
# Navigate to project
cd TESGI-Advisory-Agentic

# Start Claude Code
claude

# Process a new client
/project:intake [client-id]

# Run decision analysis
/project:analyze [client-id]

# Generate memo
/project:memo [client-id]
```

## Architecture

This project uses Claude Code with Agent Skills for specialized advisory analysis.

### Directory Structure

```
├── CLAUDE.md              # Root context (loaded every session)
├── .claude/
│   ├── settings.json      # Tool permissions
│   └── commands/          # Slash commands
├── skills/
│   ├── decision-kernel/   # TRUE/NORTH/ALIGNED analysis
│   ├── memo-generator/    # Decision memo creation
│   └── intake-processor/  # Client intake handling
├── artifacts/             # Core service documents
├── clients/               # Active client work (gitignored)
└── outputs/               # Final deliverables
```

### Advisory Council Pattern

Complex analyses use a subagent architecture:

| Agent | Role |
|-------|------|
| Truth Auditor | Information integrity assessment |
| Horizon Analyst | Long-term context evaluation |
| Coherence Evaluator | Objective-constraint alignment |
| Synthesis Lead | Final determination |

Invoke with `ultrathink` for deep reasoning.

## Governance

This project is governed by `artifacts/bridge.md`. Core constraints:

- **Advisory only** — No representation, brokerage, or agency
- **No guarantees** — Uncertainty is preserved, not minimized
- **Client authority** — Decision-making remains with client
- **Valid outcomes** — "Walk away" is a responsible result

## Decision Kernel

Every analysis applies three tests:

| Leg | Question |
|-----|----------|
| TRUE | Are facts verifiable, available, clearly bounded? |
| NORTH | Does decision make sense over time given constraints? |
| ALIGNED | Do objectives, assumptions, structure fit together? |

Failure of any leg → Pause or Avoid (never reframe to force pass).

## Dependencies

- Claude Code CLI
- pandoc (for PDF generation)
- Node.js (for docx generation if needed)

## Documentation

- `artifacts/overview.md` — Service description
- `artifacts/pricing.md` — Engagement terms
- `artifacts/bridge.md` — Governance anchor (authoritative)

---

*TESGI Advisory — Decision clarity before commitment*
