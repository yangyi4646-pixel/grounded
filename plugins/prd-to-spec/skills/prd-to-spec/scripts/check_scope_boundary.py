#!/usr/bin/env python3
"""Mechanical Scope Boundary structure check."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = [
    "Surface / Unit",
    "Affected Surfaces",
    "Non-Goals",
    "Propagation Rule",
    "Owner",
    "Source",
]

# Rows that touch the data-propagation dimension: shared / private / per-project.
DATA_SCOPE_RE = re.compile(
    r"共享|私有|按项目|per[\s-]?project|shared|private|project[\s-]?scoped",
    re.IGNORECASE,
)

# A "global / ownerless endpoint" scope conclusion that demands grep evidence.
GLOBAL_NO_OWNER_RE = re.compile(
    r"无\s*owner|没有\s*owner|no\s+owner|ownerless|scope\s*=\s*global|全局\s*作用域|作用域\s*=\s*全局",
    re.IGNORECASE,
)

# Grep-evidence presence: reuse the same surface judgment as check_grep_evidence
# (a Grep Evidence block with an rg command + a hit line or ZERO_MATCH).
def has_grep_evidence(text: str) -> bool:
    if "Grep Evidence" not in text:
        return False
    if "`rg" not in text and " rg " not in text:
        return False
    if "ZERO_MATCH" not in text and not re.search(r"[\w./-]+:\d+", text):
        return False
    return True


def parse_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_scope_boundary.py <markdown-file>", file=sys.stderr)
        return 2

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    if not re.search(r"^#{1,3}\s*(?:\d+[.)]?\s*)?Scope Boundary\b", text, re.MULTILINE):
        print("FAIL: missing Scope Boundary heading")
        return 1

    missing = [name for name in REQUIRED if name not in text]
    if missing:
        print("FAIL: missing columns: " + ", ".join(missing))
        return 1

    rows = [
        line
        for line in text.splitlines()
        if line.startswith("|") and "Affected Surfaces" not in line and "---" not in line
    ]
    data_rows = [line for line in rows if "Propagation Rule" not in line and line.count("|") >= 6]
    if not data_rows:
        print("FAIL: Scope Boundary table has no data row")
        return 1

    # Locate the Propagation Rule column index from the header row.
    header_line = next(
        (line for line in text.splitlines() if line.startswith("|") and "Propagation Rule" in line),
        "",
    )
    header_cells = parse_cells(header_line)
    prop_idx = next(
        (i for i, c in enumerate(header_cells) if "Propagation Rule" in c),
        None,
    )

    # (1) Any data row that touches shared/private/per-project data must carry a
    # non-empty Propagation Rule cell (empty → FAIL).
    if prop_idx is not None:
        empty_prop_rows: list[str] = []
        for line in data_rows:
            if not DATA_SCOPE_RE.search(line):
                continue
            cells = parse_cells(line)
            if prop_idx >= len(cells) or cells[prop_idx] in {"", "-", "—"}:
                empty_prop_rows.append(cells[0] if cells else "<row>")
        if empty_prop_rows:
            print(
                "FAIL: data-scope rows (shared/private/per-project) with empty "
                "Propagation Rule: " + ", ".join(empty_prop_rows)
            )
            return 1

    # (2) When the scope conclusion is "endpoint has no owner / scope=global",
    # require grep evidence in place (a Grep Evidence block must back the claim).
    if GLOBAL_NO_OWNER_RE.search(text) and not has_grep_evidence(text):
        print(
            "FAIL: global/ownerless scope conclusion requires Grep Evidence "
            "(Grep Evidence block with rg command + hit/ZERO_MATCH)"
        )
        return 1

    print("PASS: Scope Boundary structure present")
    print("(presence-only:结构合规,作用域选得对否交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
