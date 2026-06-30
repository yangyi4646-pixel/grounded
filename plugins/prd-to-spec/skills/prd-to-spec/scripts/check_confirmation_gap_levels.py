#!/usr/bin/env python3
"""Check P0/P1/P2 gap rows include confirmation deadlines and P1 upgrade rules."""

from __future__ import annotations

import re
import sys
from pathlib import Path

P1_RE = re.compile(r"\bP1\b", re.IGNORECASE)
P2_RE = re.compile(r"\bP2\b", re.IGNORECASE)
P0_RE = re.compile(r"\bP0\b", re.IGNORECASE)
DEADLINE_RE = re.compile(
    r"确认截止点|before\s+(?:SPEC\s+freeze|handoff|spec-to-code|affected\s+unit\s+implementation)|"
    r"before\s+implementation|现在停|Later",
    re.IGNORECASE,
)
UPGRADE_RE = re.compile(r"升级.*P0|P0.*升级|upgrade.*P0|P0.*upgrade", re.IGNORECASE)
LATER_RE = re.compile(r"\bLater\b|\bbacklog\b", re.IGNORECASE)


def table_blocks(text: str) -> list[list[list[str]]]:
    blocks: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if current:
                blocks.append(current)
                current = []
            continue
        if "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        current.append(cells)
    if current:
        blocks.append(current)
    return blocks


def level_column_index(header: list[str]) -> int | None:
    for idx, cell in enumerate(header):
        normalized = cell.strip().lower()
        if normalized in {"级别", "level", "priority"}:
            return idx
    return None


def p1_gap_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for block in table_blocks(text):
        if not block:
            continue
        header = block[0]
        level_idx = level_column_index(header)
        if level_idx is None:
            continue
        for row in block[1:]:
            if len(row) <= level_idx:
                continue
            if re.fullmatch(r"P1", row[level_idx], re.IGNORECASE):
                rows.append(row)
    return rows


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_confirmation_gap_levels.py <gaps.md>", file=sys.stderr)
        return 2

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    if not (P0_RE.search(text) or P1_RE.search(text) or P2_RE.search(text)):
        print("FAIL: missing P0/P1/P2 gap levels")
        return 1
    if not DEADLINE_RE.search(text):
        print("FAIL: missing confirmation deadline")
        return 1

    errors: list[str] = []
    for row in p1_gap_rows(text):
        row_text = " | ".join(row)
        if not DEADLINE_RE.search(row_text):
            errors.append(f"P1 row missing confirmation deadline: {row[0] if row else '<unknown>'}")
        if not UPGRADE_RE.search(row_text):
            errors.append(f"P1 row missing upgrade-to-P0 rule: {row[0] if row else '<unknown>'}")
    if errors:
        print("FAIL: " + "; ".join(errors))
        return 1

    # Non-fatal P2 lint: P2 items should route to a Later/backlog destination.
    # Conservative — this is a structure lint, so a missing Later/backlog only
    # emits a hint and never adds a FAIL (avoid false-killing a legitimate doc).
    if P2_RE.search(text) and not LATER_RE.search(text):
        print("HINT(non-fatal): P2 rows present but no Later/backlog destination word found")

    print("PASS: confirmation gap levels include deadlines and P1 upgrade rules")
    print("(presence-only:结构合规,某项分级判对否(该P0却标P1)交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
