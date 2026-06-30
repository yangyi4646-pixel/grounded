#!/usr/bin/env python3
"""Mechanical approval/lifecycle gate structure check."""

from __future__ import annotations

import re
import sys
from pathlib import Path

APPROVAL_RE = re.compile(r"审批|approval", re.IGNORECASE)
RISK_TERMS = [
    r"生命周期|lifecycle",
    r"发布|上线|publish|release",
    r"下线|offline",
    r"删除|delete|destructive",
    r"撤回|withdraw",
    r"重新提交|重复提交|resubmit|repeat submit|pending|审批中",
    r"回调|callback",
    r"第三方|外部|external|third-party|webhook|integration",
    r"配置|开关|config|setting|审批方式|审批人|endpoint",
    r"版本|version|消费|读取|consumption|read|active|生效",
]

HEADING_RE = re.compile(
    r"^#{1,3}\s*(?:\d+[.)]?\s*)?(?:Approval\s*/\s*Lifecycle\s+Gate|审批[ /／-]*生命周期确认门|生命周期审批确认门)\b",
    re.IGNORECASE | re.MULTILINE,
)

REQUIRED_COLUMNS = [
    ("Operation / Risk", "操作 / 风险"),
    ("Default is Gap", "默认必须进 gap"),
    ("Confirmed Scope", "确认范围"),
    ("Source", "来源"),
    ("Blocked Units", "阻塞单元", "影响单元"),
]

RISK_GROUPS = {
    "destructive operations": r"destructive|delete|删除|下线|offline|archive|归档",
    "batch/bulk operations": r"batch|bulk|批量",
    "pending editability / repeat submit": r"pending|审批中|锁定|可编辑|editability|重复提交|重新提交|resubmit",
    "withdraw / resubmit": r"withdraw|撤回|重新提交|resubmit",
    "callback / external handling": r"callback|回调|third-party|external|webhook|integration|第三方|外部",
    "config surface": r"config|setting|配置|开关|审批方式|审批人|endpoint|端点",
    "version / consumption read": r"version|版本|consumption|消费|读取|生效|active",
}

BAD_CELL_RE = re.compile(r"^\s*(?:|[-—]|n/?a|not applicable|tbd|todo|unknown|待定|未知|不明|无)\s*$", re.IGNORECASE)
NA_RE = re.compile(r"\b(?:n/?a|not applicable)\b|不适用", re.IGNORECASE)
REASON_RE = re.compile(r"reason|because|source|确认|用户|prd|spec|决策|证据|因为|原因|出处|不适用[:：]", re.IGNORECASE)
UNCONFIRMED_RE = re.compile(
    r"未确认|待确认|需确认|需要确认|待主体确认|待用户确认|待后续确认|"
    r"\bgap\b|存在阻塞|有阻塞|(?<!无)(?<!非)(?<!不)阻塞[:：]|blocked|blocking|pending confirmation|to be confirmed",
    re.IGNORECASE,
)
OMISSION_AS_NA_RE = re.compile(
    r"输入未|原始输入未|PRD\s*未|未提|未说明|没写|没有写|未覆盖|"
    r"not mentioned|not specified|not covered",
    re.IGNORECASE,
)
TRUE_NA_RE = re.compile(
    r"本需求不触发|不涉及该风险|无该操作入口|无该能力入口|不包含该操作|"
    r"明确不做|out[- ]of[- ]scope|non[- ]goal|not in scope",
    re.IGNORECASE,
)


def is_triggered(text: str) -> bool:
    if APPROVAL_RE.search(text):
        return True
    return any(re.search(term, text, re.IGNORECASE) for term in RISK_TERMS)


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
        if len(cells) >= 5 and not any("Operation / Risk" in cell or "操作 / 风险" in cell for cell in cells):
            rows.append(cells[:5])
    return rows


def matching_row(rows: list[list[str]], pattern: str) -> list[str] | None:
    compiled = re.compile(pattern, re.IGNORECASE)
    for row in rows:
        if compiled.search(" | ".join(row)):
            return row
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_approval_lifecycle_gate.py <markdown-file>", file=sys.stderr)
        return 2

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    if not is_triggered(text):
        print("PASS: approval/lifecycle gate not triggered")
        print("(presence-only:结构合规,确认范围业务是否正确交judge/人)")
        return 0

    if not HEADING_RE.search(text):
        print("FAIL: approval/lifecycle trigger without Approval / Lifecycle Gate")
        return 1

    missing_columns = [options[0] for options in REQUIRED_COLUMNS if not has_column(text, options)]
    if missing_columns:
        print("FAIL: missing gate columns: " + ", ".join(missing_columns))
        return 1

    missing_risks = [
        name for name, pattern in RISK_GROUPS.items()
        if not re.search(pattern, text, re.IGNORECASE)
    ]
    if missing_risks:
        print("FAIL: missing risk rows: " + ", ".join(missing_risks))
        return 1

    rows = table_rows(text)
    row_errors: list[str] = []
    for name, pattern in RISK_GROUPS.items():
        row = matching_row(rows, pattern)
        if row is None:
            row_errors.append(f"{name}: missing table row")
            continue
        if any(is_bad_cell(cell) for cell in row[1:]):
            row_errors.append(f"{name}: row has empty/placeholder cells")
        if is_bad_cell(row[3]):
            row_errors.append(f"{name}: Source is empty/placeholder")
        if is_bad_cell(row[4]):
            row_errors.append(f"{name}: Blocked Units is empty/placeholder")
        row_text = " | ".join(row)
        has_na = any(NA_RE.search(cell) for cell in row)
        if has_na and not REASON_RE.search(row_text):
            row_errors.append(f"{name}: N/A requires explicit reason/source")
        if has_na and UNCONFIRMED_RE.search(row_text):
            row_errors.append(f"{name}: N/A cannot be combined with unconfirmed/gap/blocking language")
        if has_na and OMISSION_AS_NA_RE.search(row_text) and not TRUE_NA_RE.search(row_text):
            row_errors.append(f"{name}: missing input is a gap, not N/A")
    if row_errors:
        print("FAIL: incomplete approval/lifecycle gate: " + "; ".join(row_errors))
        return 1

    print("PASS: approval/lifecycle gate present and evidence-filled")
    print("(presence-only:结构合规,确认范围业务是否正确交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
