# TESGI Packagers

Packaging and integrity helpers used by `build-memo`, `package`, and `run`.

Primary module:

- `tesgi_packagers.py`

Core exports:

- memo and PDF artifact generation
- runlog append helpers
- `write_manifest(...)`
- `write_gate_report(...)`

This directory exists to keep packaging logic separate from CLI orchestration.
