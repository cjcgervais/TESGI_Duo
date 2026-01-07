TESGI Advisory OS Spec v0.1

Intent anchor: Correct understanding is the objective. Advisory-only. Non-representational.
Primary property: Invalid states are unbuildable.

0) Definitions
Advisory Operating System

A repository that compiles client inputs into a bounded, defensible deliverable set (memo + invoice/receipt + manifest + logs) under strict governance.

Kernel Invariants

Non-negotiable logic and boundaries that must hold for any build output:

TRUE / NORTH / ALIGNED

No representation

No guarantees/predictions

“Walk away” is valid

External/client language discipline

1) Governed Self-Improvement Primitive (Locked)
Canonical rule

Agents may continuously generate and evaluate improvement proposals (security, quality, repeatability), but the TESGI operating system only updates through gated, reviewable changes that preserve kernel and boundary invariants.

Short form

Agents propose; gates decide; humans merge.

What “self-improvement” means here

A closed loop:

Propose (diff + rationale)

Evaluate (run gates/evals locally)

Verify (CI re-runs gates)

Approve & Merge (human signoff + change log)

Hard prohibition

No silent updates. No direct mutation of governance or client-facing text outside the proposal/eval/merge loop.

2) Update Tiers (Scope of “Auto-Update”)
Tier A — Safe to auto-propose routinely

Default “always on” improvements, still merged only after gates:

internal scripts/tooling

test/eval expansion

formatting/packaging reliability

dependency updates (pinned + lockfiles)

Tier B — Allowed, strict review required

Changes affecting the client trust surface:

handout wording

memo template language

pricing/engagement wording

invoice/receipt language

Rule: requires human review + a “client-surface diff summary.”

Tier C — Constitution-level changes (rare, deliberate)

Anything that affects the meaning of the service:

kernel definitions (TRUE/NORTH/ALIGNED)

role boundary rules

any scope expansion

Rule: requires ADR + explicit risk note + explicit acceptance (no “drive-by” merges).

3) Operating Modes (Codex Profiles)

You will run Codex in explicit modes. Default mode is safest.

Profile: tesgi_readonly (default)

Use for: browsing, reasoning, audits, spec work
Rules:

no write actions

no networking / web-search

no running unknown commands

Profile: tesgi_build

Use for: deterministic scaffolding, formatting, packaging, test runs
Rules:

workspace writes allowed

still no web-search by default

allowed command list only (see §5)

Profile: tesgi_research (explicit opt-in)

Use for: updating knowledge sources / best practices
Rules:

web-search allowed only here

outputs must be captured as proposals with citations or references in the ADR

never merges directly; Tier rules apply

4) Repository Structure (Compiler Pipeline)
Required top-level layout
/00_governance/
  KERNEL.md
  BOUNDARIES.md
  LANGUAGE_RULES.yml
  CHANGE_CONTROL.md
  ADR/
    ADR_0001_Governed_Self_Improvement.md

/01_templates/
  memo_template.md
  intake_form.md
  pricing_engagement.md
  handout.md
  invoice_template.docx
  receipt_template.docx

/02_client_work/
  <client_slug>/
    00_intake/
      intake.md
      intake_ack.json
    01_sources/
      sources_manifest.json
      notes.md
    02_analysis/
      true.md
      north.md
      aligned.md
    03_memo/
      memo.md
    04_package/
      memo.pdf
      invoice.pdf
      receipt.pdf
      manifest.json
      runlog.jsonl (or pointer)
    05_change_log/
      changes.md

/03_tools/
  tesgi (cli entry)
  validators/
  packagers/
  scripts/

/04_evals/
  golden_cases/
  regression_suite.yml

/runs/
  YYYYMMDD_<client_slug>_<run_id>/
    manifest.json
    gate_report.json
    build_log.txt
    codex_session_pointer.txt

Structural invariants

A client build cannot exist without 00_intake/intake_ack.json

north.md cannot be produced unless true.md exists

aligned.md cannot be produced unless north.md exists

A package cannot be produced unless all gates pass (§5)

5) Gates (What Must Always Pass)

Gates are the core of “magnificent and safe.” They are not optional.

Gate A — Kernel completeness

TRUE/NORTH/ALIGNED files exist

Each contains:

observations

explicit uncertainties

risk notes

Gate B — Decision state validity

Memo must include exactly one:

Proceed

Pause

Avoid/Walk Away

And must satisfy:

Proceed invalid if any kernel leg flags “unbounded uncertainty” or missing required facts

Pause must include a “Missing Information List” (explicit)

Avoid must include “Rationale Summary” (explicit)

Gate C — Boundary compliance (language lint)

Block prohibited terms and implied promises (configurable list), e.g.:

recommend / guarantee / approve / will / assured

“we’ll handle” / “we will coordinate” / “on your behalf” (representation markers)

Also require presence of:

“What This Memo Does Not Say”

“Non-representational advisory only” disclaimer

Gate D — Packaging integrity

PDFs generated successfully

Manifest includes:

file hashes

timestamps

versions

tool versions

Gate E — Regression suite

Golden-case inputs must still produce compliant memos (structure + required disclaimers + no forbidden language).

6) Build Commands (Command Surface)

Codex agents should be constrained to a small “safe command surface.”

Required CLI commands (human + Codex)

tesgi init-client <slug>

tesgi validate <slug>

tesgi build-memo <slug>

tesgi package <slug>

tesgi run <slug> (validate + build + package)

tesgi eval (golden regression suite)

Allowed shell commands for agents (strict)

read-only: ls, cat, sed -n, rg, find

build: python -m ..., node ... (only repo scripts), pandoc/PDF toolchain (if used), git status, git diff

never: arbitrary curl/wget in build mode, never “chmod 777”, never deleting outside workspace

(We’ll encode this as policy and as checks inside tesgi.)

7) Change Control (ADR + Merge Discipline)
ADR required for:

Tier B and Tier C always

Tier A if it changes gates, toolchain, or defaults

ADR must include:

Summary

Why (risk/benefit)

What changes

Tests/evals run

Risks + rollback plan

Client-surface impact (if any)

Merge rule

No merge unless:

all gates pass

ADR present when required

change log updated

8) Agent Responsibilities (Bounded)

Agents can:

scaffold and refactor implementation under gates

propose governance changes via ADR

expand eval suites

improve packaging reproducibility

generate run manifests/log pointers

Agents cannot:

ship client deliverables without passing gates

weaken boundaries

modify Tier C without explicit ADR + human acceptance

introduce persuasive/outcome language

9) Success Criteria (What “cutting edge” means here)

The system is successful when:

A new client workspace can be created in < 1 minute

A memo cannot be packaged if it violates boundaries

A tired day can’t produce a risky deliverable

Every delivered PDF can be tied to a manifest + run record

Improvements continuously accumulate without drift