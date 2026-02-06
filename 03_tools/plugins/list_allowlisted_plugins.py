#!/usr/bin/env python3
"""Print allowlisted plugin specs from governance config."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tesgi.plugins.manager import load_allowlist


def main() -> int:
    allowlist_path = ROOT / "00_governance" / "PLUGIN_ALLOWLIST.json"
    specs = load_allowlist(allowlist_path)
    payload = {
        "allowlist_path": allowlist_path.as_posix(),
        "plugins": [
            {
                "id": spec.plugin_id,
                "type": spec.plugin_type,
                "module": spec.module,
                "class": spec.class_name,
                "version": spec.version,
                "enabled_by_default": spec.enabled_by_default,
            }
            for spec in sorted(specs.values(), key=lambda item: item.plugin_id)
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
