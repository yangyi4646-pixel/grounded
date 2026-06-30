#!/usr/bin/env python3
"""Mechanical information-ownership matrix structure check."""

from __future__ import annotations

import re
import sys
from pathlib import Path

TRIGGER_RE = re.compile(
    r"多对象|绑定|映射|上游|下游|消费对象|展开|收起|头部|摘要|详情|卡片|字段对齐|"
    r"multi-object|binding|mapping|upstream|downstream|expanded|collapsed|header|summary|detail",
    re.IGNORECASE,
)

HEADING_RE = re.compile(
    r"^#{1,3}\s*(?:\d+[.)]?\s*)?(?:Information\s+Ownership\s+Matrix|信息归属矩阵|对象归属矩阵)\b",
    re.IGNORECASE | re.MULTILINE,
)

REQUIRED_COLUMNS = [
    ("Domain / Layer", "信息域 / 层级", "归属"),
    ("Ownership Rule", "归属规则"),
    ("Information", "信息"),
    ("Display Responsibility", "展示职责"),
    ("Exclusion / Dedupe Rule", "排除 / 去重规则", "去重"),
    ("Source", "来源"),
]

REQUIRED_ROWS = {
    "current main object": r"Current main object|当前页面主对象|当前主对象|主对象",
    "upstream object": r"Upstream object|上游对象",
    "downstream consumer object": r"Downstream consumer object|下游消费对象|消费对象",
    "relation-only information": r"Relation-only information|关系态信息|绑定关系|关系信息",
    "full-detail-only information": r"Full-detail-only information|完整详情页|完整详情",
}

REQUIRED_SECTIONS = [
    r"Current page main object|当前页面主对象",
    r"Header summary responsibility|头部摘要职责",
    r"Expanded-detail responsibility|展开区职责|展开明细职责",
    r"Do-not-repeat rule|不重复展示规则|去重规则",
]

BAD_CELL_RE = re.compile(r"^\s*(?:|[-—]|n/?a|not applicable|tbd|todo|unknown|待定|未知|不明|无)\s*$", re.IGNORECASE)
NA_RE = re.compile(r"\b(?:n/?a|not applicable)\b|不适用", re.IGNORECASE)
# A reason must carry substantive content after the keyword; bare "prd"/"spec"/"用户" no longer count.
REASON_RE = re.compile(
    r"因为\S{2,}"
    r"|不适用\s*[（(：:]\s*\S{2,}"
    r"|(?:来源|出处|原因|理由|reason|source|because)\s*[:：]?\s*\S{2,}"
    r"|确认\S{2,}"
    r"|决策\S{2,}"
    r"|证据\S{2,}",
    re.IGNORECASE,
)


def has_column(text: str, options: tuple[str, ...]) -> bool:
    return any(option in text for option in options)


def is_bad_cell(value: str) -> bool:
    return BAD_CELL_RE.match(value.strip()) is not None


def table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) >= 6 and not any("Domain / Layer" in cell or "信息域" in cell for cell in cells):
            rows.append(cells[:6])
    return rows


def matching_row(rows: list[list[str]], pattern: str) -> list[str] | None:
    compiled = re.compile(pattern, re.IGNORECASE)
    for row in rows:
        if compiled.search(" | ".join(row)):
            return row
    return None


def main_object_is_filled(text: str) -> bool:
    match = re.search(r"(?:Current page main object|当前页面主对象)(?:\s*\([^)]*\))?\s*[:：]\s*(.+)", text, re.IGNORECASE)
    return bool(match and not is_bad_cell(match.group(1)))


def section_has_content(text: str, heading: str) -> bool:
    match = re.search(
        rf"(?:{heading})(?:\s*\([^)]*\))?\s*[:：]?\s*\n(?P<body>.*?)(?:\n\s*(?:Header summary responsibility|头部摘要职责|Expanded-detail responsibility|展开区职责|展开明细职责|Do-not-repeat rule|不重复展示规则|去重规则|Current page main object|当前页面主对象|##|\Z))",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return False
    body = "\n".join(line.strip("- ").strip() for line in match.group("body").splitlines()).strip()
    return bool(body and not is_bad_cell(body))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_information_ownership_matrix.py <markdown-file>", file=sys.stderr)
        return 2

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    if not TRIGGER_RE.search(text):
        print("PASS: information ownership matrix not triggered")
        print("(presence-only:结构合规,去重/归属语义判对否交judge/人)")
        return 0

    if not HEADING_RE.search(text):
        print("FAIL: multi-object/detail trigger without Information Ownership Matrix")
        return 1

    missing_columns = [options[0] for options in REQUIRED_COLUMNS if not has_column(text, options)]
    if missing_columns:
        print("FAIL: missing ownership columns: " + ", ".join(missing_columns))
        return 1

    missing_rows = [name for name, pattern in REQUIRED_ROWS.items() if not re.search(pattern, text, re.IGNORECASE)]
    if missing_rows:
        print("FAIL: missing ownership rows: " + ", ".join(missing_rows))
        return 1

    missing_sections = [pattern for pattern in REQUIRED_SECTIONS if not re.search(pattern, text, re.IGNORECASE)]
    if missing_sections:
        print("FAIL: missing responsibility/dedupe sections")
        return 1

    if not main_object_is_filled(text):
        print("FAIL: current page main object is empty or placeholder")
        return 1

    rows = table_rows(text)
    row_errors: list[str] = []
    for name, pattern in REQUIRED_ROWS.items():
        row = matching_row(rows, pattern)
        if row is None:
            row_errors.append(f"{name}: missing table row")
            continue
        if any(is_bad_cell(cell) for cell in row[1:]):
            row_errors.append(f"{name}: row has empty/placeholder cells")
        if is_bad_cell(row[5]):
            row_errors.append(f"{name}: Source is empty/placeholder")
        if name == "current main object" and any(NA_RE.search(cell) for cell in row):
            # Load-bearing row: N/A is never acceptable here.
            row_errors.append(f"{name}: main object row must not use N/A")
        elif any(NA_RE.search(cell) for cell in row) and not REASON_RE.search(" | ".join(row)):
            row_errors.append(f"{name}: N/A requires explicit reason/source")
    if row_errors:
        print("FAIL: incomplete ownership matrix: " + "; ".join(row_errors))
        return 1

    required_bodies = {
        "header summary responsibility": r"Header summary responsibility|头部摘要职责",
        "expanded-detail responsibility": r"Expanded-detail responsibility|展开区职责|展开明细职责",
        "do-not-repeat rule": r"Do-not-repeat rule|不重复展示规则|去重规则",
    }
    missing_bodies = [name for name, pattern in required_bodies.items() if not section_has_content(text, pattern)]
    if missing_bodies:
        print("FAIL: empty responsibility/dedupe section bodies: " + ", ".join(missing_bodies))
        return 1

    print("PASS: information ownership matrix present and evidence-filled")
    print("(presence-only:结构合规,去重/归属语义判对否交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
