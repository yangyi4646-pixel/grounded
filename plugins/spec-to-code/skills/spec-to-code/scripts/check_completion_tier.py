#!/usr/bin/env python3
"""Mechanical completion-tier honesty check."""

from __future__ import annotations

import re
import sys
from pathlib import Path

TIERS = [
    "Implementation complete",
    "Local validation complete",
    "Visual alignment complete",
    "Usability walkthrough complete",
    "Design-side release complete",
]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_completion_tier.py <markdown-file>", file=sys.stderr)
        return 2

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    if not any(tier in text for tier in TIERS):
        print("FAIL: no completion tier stated")
        return 1

    unchecked = re.search(r"\bunchecked\b|未检|未执行|not run", text, re.IGNORECASE)
    done_claim = re.search(
        r"生成好了|全部完成|都完成了|全部通过|全过|搞定|搞好了|ok了|大功告成|"
        r"\bdone\b|\bready\b|\bshipped\b|all\s+(?:gates\s+)?pass(?:ed)?",
        text,
        re.IGNORECASE,
    )
    if unchecked and done_claim:
        print("FAIL: unchecked gates with overall completion/pass claim")
        return 1

    print("PASS: completion tier structure present")
    print("(presence-only:结构合规,层级是否真达到 / 证据真假交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
