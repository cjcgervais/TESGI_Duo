#!/usr/bin/env python3
"""Print orchestration stages and contract requirements."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tesgi.orchestration.contracts import STAGE_CONTRACTS
from tesgi.orchestration.states import NEXT_STAGE, PREDECESSOR, STAGES


def main() -> int:
    payload = {
        "stages": [
            {
                "name": stage,
                "previous": PREDECESSOR[stage],
                "next": NEXT_STAGE[stage],
                "required_files": list(STAGE_CONTRACTS[stage].required_files),
                "required_gates": list(STAGE_CONTRACTS[stage].required_gates),
            }
            for stage in STAGES
        ]
    }
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
