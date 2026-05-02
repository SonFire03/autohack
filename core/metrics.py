from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from config.settings import EXECUTION_LOG_FILE


def usage_metrics(path: Path = EXECUTION_LOG_FILE) -> dict[str, Any]:
    if not path.exists():
        return {"total": 0, "top_commands": [], "fail_by_tool": [], "avg_duration_by_category": []}

    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except Exception:
            continue

    top_commands = Counter(e.get("id", "") for e in events if e.get("id")).most_common(10)
    fail_by_tool = Counter(e.get("tool", "") for e in events if e.get("exit_code", 0) != 0 and e.get("tool")).most_common(10)

    sums = defaultdict(float)
    counts = defaultdict(int)
    for e in events:
        cat = e.get("category")
        dur = e.get("duration_s")
        if cat and isinstance(dur, (int, float)):
            sums[cat] += float(dur)
            counts[cat] += 1

    avg_duration_by_category = sorted(
        ((cat, round(sums[cat] / counts[cat], 3)) for cat in counts),
        key=lambda item: item[1], reverse=True,
    )

    return {
        "total": len(events),
        "top_commands": top_commands,
        "fail_by_tool": fail_by_tool,
        "avg_duration_by_category": avg_duration_by_category,
    }
