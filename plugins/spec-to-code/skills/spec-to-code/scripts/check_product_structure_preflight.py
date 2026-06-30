#!/usr/bin/env python3
"""Mechanical product-structure preflight check for multi-object UI work."""

from __future__ import annotations

import re
import sys
from pathlib import Path

TRIGGER_RE = re.compile(
    r"多对象|绑定|映射|字段对齐|展开|收起|卡片|表格|详情|头部|摘要|"
    r"multi-object|binding|mapping|field alignment|expanded|collapsed|card|table|detail|header|summary",
    re.IGNORECASE,
)

HEADING_RE = re.compile(
    r"^#{1,3}\s*(?:\d+[.)]?\s*)?(?:Product\s+Structure\s+Preflight|产品结构实现前检查)\b",
    re.IGNORECASE | re.MULTILINE,
)

REQUIRED_ITEMS = {
    "current page main object": r"Current page main object|当前页面主对象|主对象",
    "information ownership matrix": r"Information Ownership Matrix|信息归属矩阵|对象归属矩阵",
    "header summary responsibility": r"Header summary responsibility|头部摘要职责",
    "expanded-detail responsibility": r"Expanded-detail responsibility|展开区职责|展开明细职责",
    "do-not-repeat display rule": r"Do-not-repeat display rule|不重复展示规则|去重规则",
    "information this page does not carry": r"Information this page does not carry|当前页面不承载的信息|不承载的信息",
}

BAD_CELL_RE = re.compile(r"^\s*(?:|[-—]|tbd|todo|unknown|待定|未知|不明|无)\s*$", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"yes\s*/\s*no\s*/\s*n/?a|是\s*/\s*否", re.IGNORECASE)
YES_RE = re.compile(r"^(?:yes|y|是|有|present)$", re.IGNORECASE)
NO_RE = re.compile(r"^(?:no|n|否|missing|absent)$", re.IGNORECASE)
NA_RE = re.compile(r"^(?:n/?a|not applicable|不适用)$", re.IGNORECASE)
# Aligned with check_information_ownership_matrix.py: a reason must carry
# substantive content after the keyword (\S{2,}); bare prd/spec/用户/确认 no
# longer count as a reason.
REASON_RE = re.compile(
    r"因为\S{2,}"
    r"|不适用\s*[（(：:]\s*\S{2,}"
    r"|(?:来源|出处|原因|理由|reason|source|anchor|because)\s*[:：]?\s*\S{2,}"
    r"|确认\S{2,}"
    r"|决策\S{2,}"
    r"|证据\S{2,}",
    re.IGNORECASE,
)
STOP_RE = re.compile(r"stop|return to prd-to-spec|回到\s*prd-to-spec|停止|阻塞|blocked|affected|受影响", re.IGNORECASE)


def is_bad_cell(value: str) -> bool:
    value = value.strip()
    return BAD_CELL_RE.match(value) is not None or PLACEHOLDER_RE.search(value) is not None


def table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) >= 4 and not any("Required SPEC Contract" in cell or "Present?" in cell for cell in cells):
            while len(cells) < 5:
                cells.append("")
            rows.append(cells[:5])
    return rows


def matching_row(rows: list[list[str]], pattern: str) -> list[str] | None:
    compiled = re.compile(pattern, re.IGNORECASE)
    for row in rows:
        if compiled.search(row[0]):
            return row
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_product_structure_preflight.py <markdown-file>", file=sys.stderr)
        return 2

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    if not TRIGGER_RE.search(text):
        print("PASS: product structure preflight not triggered")
        print("(presence-only:结构合规,SPEC是否真交付结构(由上游矩阵真值兜)交judge/人)")
        return 0

    if not HEADING_RE.search(text):
        print("FAIL: multi-object/detail UI trigger without Product Structure Preflight")
        return 1

    missing = [name for name, pattern in REQUIRED_ITEMS.items() if not re.search(pattern, text, re.IGNORECASE)]
    if missing:
        print("FAIL: missing preflight items: " + ", ".join(missing))
        return 1

    rows = table_rows(text)
    row_errors: list[str] = []
    for name, pattern in REQUIRED_ITEMS.items():
        row = matching_row(rows, pattern)
        if row is None:
            row_errors.append(f"{name}: missing table row")
            continue
        present, anchor, decision, affected = row[1], row[2], row[3], row[4]
        if is_bad_cell(present):
            row_errors.append(f"{name}: Present? is empty or placeholder")
            continue
        if YES_RE.match(present):
            if is_bad_cell(anchor):
                row_errors.append(f"{name}: yes requires SPEC Anchor / Source")
            if is_bad_cell(decision):
                row_errors.append(f"{name}: yes requires Implementation Decision")
        elif NO_RE.match(present):
            stop_context = " | ".join([decision, affected])
            if not STOP_RE.search(stop_context):
                row_errors.append(f"{name}: no requires stop/return decision")
            if is_bad_cell(affected):
                row_errors.append(f"{name}: no requires affected/blocked path")
        elif NA_RE.match(present):
            if not REASON_RE.search(" | ".join([anchor, decision, affected])):
                row_errors.append(f"{name}: N/A requires explicit reason/source")
        else:
            row_errors.append(f"{name}: Present? must be yes/no/N/A")
    if row_errors:
        print("FAIL: incomplete product structure preflight: " + "; ".join(row_errors))
        return 1

    print("PASS: product structure preflight present and decision-filled")
    print("(presence-only:结构合规,SPEC是否真交付结构(由上游矩阵真值兜)交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
