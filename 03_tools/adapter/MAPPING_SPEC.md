# Claude <-> TESGI Workspace Mapping

This file defines file-level mapping for the Duo Advisory adapter scripts.

## Canonical Direction

`claude_to_tesgi.py`:

| Claude source | TESGI target |
|---|---|
| `clients/<client_id>/intake.md` | `02_client_work/<slug>/00_intake/intake.md` |
| `clients/<client_id>/analysis/true.md` | `02_client_work/<slug>/02_analysis/true.md` |
| `clients/<client_id>/analysis/north.md` | `02_client_work/<slug>/02_analysis/north.md` |
| `clients/<client_id>/analysis/aligned.md` | `02_client_work/<slug>/02_analysis/aligned.md` |
| `clients/<client_id>/memo.md` | `02_client_work/<slug>/03_memo/Decision_Memo.md` |
| `clients/<client_id>/sources/**/*` | `02_client_work/<slug>/01_sources/**/*` |

Additional generated file:

- `02_client_work/<slug>/00_intake/intake_ack.json`
  - `status = "ingested_from_claude"`
  - `source_client_id = <client_id>`
  - `slug = <slug>`

## Reverse Direction

`tesgi_to_claude.py`:

| TESGI source | Claude target |
|---|---|
| `02_client_work/<slug>/00_intake/intake.md` | `clients/<client_id>/intake.md` |
| `02_client_work/<slug>/02_analysis/true.md` | `clients/<client_id>/analysis/true.md` |
| `02_client_work/<slug>/02_analysis/north.md` | `clients/<client_id>/analysis/north.md` |
| `02_client_work/<slug>/02_analysis/aligned.md` | `clients/<client_id>/analysis/aligned.md` |
| `02_client_work/<slug>/03_memo/Decision_Memo.md` | `clients/<client_id>/memo.md` |
| `02_client_work/<slug>/01_sources/**/*` | `clients/<client_id>/sources/**/*` |

Client ID resolution:

- If `--client-id` is provided, use it.
- Else if `00_intake/intake_ack.json` has `source_client_id`, use it.
- Else default to `<slug>`.

## Slug Rules

- Default slug is generated from `<client_id>`:
  - lowercase
  - replace non `[a-z0-9_-]` chars with `-`
  - collapse duplicate `-`
  - trim leading/trailing `-`
- Override with `--slug` if required.

## Safety Rules

- Both scripts fail on existing target directory unless `--force` is provided.
- Both scripts print JSON summaries to support deterministic logs.
