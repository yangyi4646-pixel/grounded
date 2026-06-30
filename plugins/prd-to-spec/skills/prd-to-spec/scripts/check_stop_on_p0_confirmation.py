#!/usr/bin/env python3
"""Check that P0 confirmation blockers stop full SPEC generation."""

from __future__ import annotations

import re
import sys
from pathlib import Path

P0_RE = re.compile(
    r"P0|硬确认|硬卡点|阻塞契约|主对象|对象边界|生命周期|消费读取|权限|迁移|引用完整性|"
    r"IA|信息架构|稳定\s*id|存储键",
    re.IGNORECASE,
)

STOP_RE = re.compile(
    r"Stop-on-P0|P0\s*确认|停在确认门|暂停生成完整\s*SPEC|等待用户确认|待主体确认|"
    r"confirmation request|hard confirmation",
    re.IGNORECASE,
)

FULL_SPEC_RE = re.compile(
    r"^##\s*(?:§0|0\.|单元索引|单元\s*\d+|Scope Boundary|完整性矩阵|验收|决策日志)",
    re.MULTILINE,
)

PROHIBITED_FULL_SECTIONS = re.compile(
    r"^##\s*单元\s*\d+|^###\s*区域装配|^###\s*交互矩阵|^###\s*验收",
    re.MULTILINE,
)


def read(paths: list[str]) -> str:
    parts: list[str] = []
    for path in paths:
        parts.append(Path(path).read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_stop_on_p0_confirmation.py <output-or-confirmation.md> [more.md ...]", file=sys.stderr)
        return 2

    text = read(sys.argv[1:])
    has_p0 = bool(P0_RE.search(text))
    if not has_p0:
        print("PASS: no P0 confirmation blocker detected")
        print("(presence-only:结构合规,P0是否真命中 / 占位是否真占位交judge/人)")
        return 0

    if not STOP_RE.search(text):
        print("FAIL: P0-like blocker present without explicit Stop-on-P0 confirmation request")
        return 1

    if PROHIBITED_FULL_SECTIONS.search(text):
        print("FAIL: P0 blocker present but full unit/spec sections were generated")
        return 1

    if FULL_SPEC_RE.search(text) and not re.search(r"⚠️\s*待确认|占位|skeleton|骨架", text, re.IGNORECASE):
        print("FAIL: P0 blocker present but SPEC-like sections are not clearly placeholder-only")
        return 1

    print("PASS: P0 blocker stops full SPEC generation")
    print("(presence-only:结构合规,P0是否真命中 / 占位是否真占位交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
