#!/usr/bin/env python3
"""Mechanical completeness-matrix structure check."""

from __future__ import annotations

import re
import sys
from pathlib import Path

# A gap marker inside a single cell, e.g. ⚠️G1 / ⚠️ G12.
GAP_MARKER_RE = re.compile(r"⚠️\s*G\d+")

REQUIRED_COLUMNS = [
    "操作",
    "权限",
    "空态",
    "错误",
    "状态",
    "数据一致性",
    "消费",
]

REQUIRED_OPS = ["查", "增", "改", "删"]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_gap_matrix.py <markdown-file>", file=sys.stderr)
        return 2

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    if "完整性矩阵" not in text:
        print("FAIL: missing completeness matrix heading")
        return 1

    header = next((line for line in text.splitlines() if "操作" in line and "关注点" in line), "")
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in header]
    if missing_columns:
        print("FAIL: missing matrix columns: " + ", ".join(missing_columns))
        return 1

    rows = [line for line in text.splitlines() if line.startswith("|") and "---" not in line]
    missing_ops = [op for op in REQUIRED_OPS if not any(f"| {op}" in row or f"|{op}" in row for row in rows)]
    if missing_ops:
        print("FAIL: missing operation rows: " + ", ".join(missing_ops))
        return 1

    malformed_rows: list[str] = []
    empty_cells: list[str] = []
    mixed_cells: list[str] = []
    in_matrix_block = False
    for line in text.splitlines():
        stripped = line.strip()
        is_table_row = stripped.startswith("|")
        if is_table_row and "操作" in stripped and "关注点" in stripped:
            # Matrix header: start a fresh block (supports multiple grids).
            in_matrix_block = True
            continue
        if not in_matrix_block:
            continue
        if not is_table_row:
            # Blank line or non-table content closes the current matrix block.
            in_matrix_block = False
            continue
        if "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        label = cells[0] if cells else ""
        if len(cells) < 7:
            malformed_rows.append(label)
        elif any(cell == "" for cell in cells[1:]):
            empty_cells.append(label)
        # One-cell-mixing lower bound: a single cell carrying >=2 ⚠️Gn gap
        # markers is two gaps crammed into one slot — each gap needs its own cell.
        for cell in cells:
            if len(GAP_MARKER_RE.findall(cell)) >= 2:
                mixed_cells.append(f"{label}:{cell}")
    if malformed_rows:
        print("FAIL: malformed matrix rows (fewer than 7 cells): " + ", ".join(malformed_rows))
        return 1
    if empty_cells:
        print("FAIL: empty matrix cells in rows: " + ", ".join(empty_cells))
        return 1
    if mixed_cells:
        print("FAIL: cell mixes >=2 gap markers (⚠️Gn): " + ", ".join(mixed_cells))
        return 1

    print("PASS: completeness matrix structure present")
    print("(presence-only:结构合规,格内业务对错与是否一格混装交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
