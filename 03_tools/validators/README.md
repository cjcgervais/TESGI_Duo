# TESGI Validators

Runtime gate logic used by `python -m tesgi validate`.

Primary module:

- `tesgi_gate_validators.py`

Core exports:

- `run_gates(...)`
- `print_results(...)`
- gate functions (`O`, `A`, `B`, `C`, `D`, `E`)

This directory exists to keep validator logic separate from CLI orchestration.
