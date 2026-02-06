---
name: intake
description: Process client intake and prepare analysis workspace
arguments:
  - name: client-id
    description: Unique identifier for the client
    required: true
---

# /project:intake — Client Intake Processing

Process a new client intake and prepare the analysis workspace.

## Execution Steps

1. **Validate Client ID**
   - Ensure client-id is provided and unique
   - Check if workspace already exists

2. **Load Intake Data**
   - Read intake form from provided source
   - Or prompt for intake information

3. **Run Intake Processor Skill**
   ```
   Load: skills/intake-processor/SKILL.md
   Reference: skills/intake-processor/references/intake-validation.md
   Form template: artifacts/intake-form.md
   ```

4. **Create Client Workspace**
   ```
   clients/$arguments.client-id/
   ├── intake.md
   ├── analysis/
   │   ├── true.md
   │   ├── north.md
   │   └── aligned.md
   └── sources/
   ```

5. **Validate Completeness**
   - Check all required fields
   - Flag any red flags
   - Confirm engagement terms

6. **Report Status**
   - Output validation result
   - List any clarifications needed
   - Confirm readiness for analysis

## Governance Reference

- Bridge document: artifacts/bridge.md
- Service overview: artifacts/overview.md
- Pricing terms: artifacts/pricing.md

## Usage

```bash
/project:intake [client-id]
```

## Example

```bash
/project:intake smith-2024-001
```

This will create the workspace at `clients/smith-2024-001/` and process the intake.
