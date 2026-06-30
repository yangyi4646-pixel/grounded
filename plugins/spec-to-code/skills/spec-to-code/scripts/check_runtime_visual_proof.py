#!/usr/bin/env python3
"""Mechanical runtime visual proof structure check."""

from __future__ import annotations

import re
import sys
from pathlib import Path

TRIGGER_RE = re.compile(
    r"Visual Contract|Visual Proof|Runtime Visual Proof|style-affecting|style change|"
    r"样式|视觉|颜色|圆角|字号|字重|间距|tag|badge|tooltip|table|icon|typography|computed style",
    re.IGNORECASE,
)

HEADING_RE = re.compile(
    r"^#{1,3}\s*(?:\d+[.)]?\s*)?(?:Runtime\s+Visual\s+Proof|运行时视觉证明)\b",
    re.IGNORECASE | re.MULTILINE,
)

REQUIRED_COLUMNS = [
    ("Surface", "界面"),
    ("Rendered Node", "渲染节点"),
    ("Token / Style Readback", "Token / Style Readback", "样式回读", "token"),
    ("Computed / Screenshot Evidence", "Computed / Screenshot Evidence", "计算样式", "截图"),
    ("Result", "结果"),
]

PROOF_TERMS = [
    r"computed style",
    r"getComputedStyle",
    r"screenshot",
    r"Playwright",
    r"DOM",
    r"bounding",
    r"bbox",
    r"token value",
    r"计算样式",
    r"截图",
    r"节点",
    r"边界框",
    r"unchecked",
    r"未检",
    r"N/A",
    r"不适用",
]

UNCHECKED_RE = re.compile(r"\bunchecked\b|未检|未执行|not\s+run", re.IGNORECASE)
# A same-row reason backing an unchecked item (mirrors the approval gate's
# N/A + reason logic): a keyword followed by substantive content.
REASON_RE = re.compile(
    r"因为\S{2,}"
    r"|原因\s*[:：]?\s*\S{2,}"
    r"|理由\s*[:：]?\s*\S{2,}"
    r"|(?:reason|because)\s*[:：]?\s*\S{2,}"
    r"|待\S{2,}"
    r"|阻塞\S{2,}|blocked\s+\S{2,}"
    r"|后续\S{2,}|defer\S*\s*\S{2,}|backlog",
    re.IGNORECASE,
)


def has_column(text: str, options: tuple[str, ...]) -> bool:
    return any(option in text for option in options)


def table_rows(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith("|") and "---" not in line
    ]


def unchecked_rows_missing_reason(text: str) -> list[str]:
    """Find Runtime Visual Proof rows marked unchecked but with no same-row reason."""
    bad: list[str] = []
    for row in table_rows(text):
        if "Rendered Node" in row or "渲染节点" in row or "Surface" in row:
            continue  # header row
        if not UNCHECKED_RE.search(row):
            continue
        if not REASON_RE.search(row):
            cells = [c.strip() for c in row.strip("|").split("|")]
            bad.append(cells[0] if cells else "<row>")
    return bad


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_runtime_visual_proof.py <markdown-file>", file=sys.stderr)
        return 2

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    if not TRIGGER_RE.search(text):
        print("PASS: runtime visual proof not triggered")
        print("(presence-only:结构合规,渲染语义(色彩角色/字重)是否正确交judge/人)")
        return 0

    if not HEADING_RE.search(text):
        print("FAIL: visual/style trigger without Runtime Visual Proof")
        return 1

    missing_columns = [options[0] for options in REQUIRED_COLUMNS if not has_column(text, options)]
    if missing_columns:
        print("FAIL: missing Runtime Visual Proof columns: " + ", ".join(missing_columns))
        return 1

    if not any(re.search(pattern, text, re.IGNORECASE) for pattern in PROOF_TERMS):
        print("FAIL: Runtime Visual Proof has no computed/screenshot/DOM/token/unchecked evidence")
        return 1

    # An unchecked visual item must carry a same-row reason (mirrors the
    # approval gate's N/A + reason rule); unchecked with no reason → FAIL.
    missing_reason = unchecked_rows_missing_reason(text)
    if missing_reason:
        print("FAIL: unchecked Runtime Visual Proof rows without same-row reason: " + ", ".join(missing_reason))
        return 1

    print("PASS: runtime visual proof structure present")
    print("(presence-only:结构合规,渲染语义(色彩角色/字重)是否正确交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
