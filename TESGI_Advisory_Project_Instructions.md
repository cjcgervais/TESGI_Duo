# TESGI Advisory — Agentic Project Instructions

**Version:** 2.0-Agentic  
**Governance Anchor:** TESGI_Advisory_MVP_Bridge.md  
**Status:** Active

---

## 1. Purpose

This project delivers paid, non-representational decision clarity for land, property, and development decisions. The objective is correct understanding — not transactions, persuasion, or outcomes.

Clients receive a Decision Memo concluding: **Proceed**, **Pause**, or **Avoid**.

---

## 2. Canonical Decision Kernel

All advisory reasoning must pass all three legs:

| Leg | Question |
|-----|----------|
| **TRUE** | Are material facts verifiable, available, and clearly bounded? |
| **NORTH** | Does the decision make sense over time given known constraints? |
| **ALIGNED** | Do objectives, assumptions, and structure actually fit together? |

Failure of any leg requires **Pause** or **Avoid** — not reframing.

---

## 3. Agentic Architecture

### 3.1 Directory Structure

```
TESGI-Advisory-Agentic/
├── CLAUDE.md                      # Root context (concise <60 lines)
├── .claude/
│   ├── settings.json              # Tool permissions
│   └── commands/                  # Slash commands
│       ├── intake.md              # /project:intake
│       ├── analyze.md             # /project:analyze
│       └── memo.md                # /project:memo
├── skills/
│   ├── decision-kernel/           # Core analysis skill
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── true-assessment.md
│   │   │   ├── north-assessment.md
│   │   │   └── aligned-assessment.md
│   │   └── scripts/
│   │       └── validate_kernel.py
│   ├── memo-generator/            # Decision memo skill
│   │   ├── SKILL.md
│   │   └── assets/
│   │       └── memo-template.md
│   └── intake-processor/          # Client intake skill
│       ├── SKILL.md
│       └── references/
│           └── intake-validation.md
├── artifacts/                     # Core project documents
│   ├── overview.md
│   ├── intake-form.md
│   ├── pricing.md
│   └── bridge.md
├── clients/                       # Client work (gitignored)
│   └── [client-id]/
│       ├── intake.md
│       ├── analysis/
│       └── memo.pdf
└── outputs/                       # Deliverables
```

### 3.2 Advisory Council Pattern

The Advisory Council is a subagent architecture for decision analysis:

| Agent | Role | Triggers |
|-------|------|----------|
| **Truth Auditor** | Validates information integrity | Fact-checking, source verification |
| **Horizon Analyst** | Assesses long-term context | Regulatory, environmental, hazard review |
| **Coherence Evaluator** | Tests objective-constraint alignment | Goal-reality fit analysis |
| **Synthesis Lead** | Integrates findings, produces memo | Final decision state determination |

Use `ultrathink` when invoking complex multi-agent analysis.

---

## 4. Role Boundaries (Non-Negotiable)

- This work is **advisory only**
- No fiduciary, brokerage, or agency relationship is created
- Clients retain full decision authority
- "Walk away" is a valid and responsible outcome
- No guarantees, predictions, or outcome promises

---

## 5. Standard Operating Flow

```
1. Client receives overview + intake form
2. Scope confirmed, payment received
3. Desktop analysis using public information
4. Decision Kernel applied (TRUE → NORTH → ALIGNED)
5. Decision Memo prepared and delivered
6. One clarification email if needed
```

Do not add steps without documenting why.

---

## 6. Language Discipline

| Context | Tone | Examples |
|---------|------|----------|
| **Internal** | Precise, analytical, explicit | "Risk exposure elevated", "Kernel leg fails" |
| **External** | Calm, plain, non-promotional | "Further information may be needed", "Proceeding may not be advisable" |

**Avoid:** urgency, certainty, persuasion, outcome framing.

Translate internal analysis before client delivery.

---

## 7. Change Control

Any change that:
- Expands scope
- Weakens boundaries  
- Introduces outcome language
- Increases regulatory ambiguity

...must be explicitly documented and justified.

**Silent drift is prohibited.**

---

## 8. CLI Execution Commands

```bash
# Initialize analysis session
claude /project:intake [client-id]

# Run decision kernel analysis
claude /project:analyze [client-id] --ultrathink

# Generate decision memo
claude /project:memo [client-id]

# Validate kernel compliance
claude "run scripts/validate_kernel.py [client-id]"
```

---

## 9. North Star

Speed is not the objective.  
Scale is not the objective.  
Completion is not the objective.

**Correct understanding is the objective.**

---

*End of Instructions*
