#!/usr/bin/env python3
"""N3 · Reuse-first list presence check (presence-only).

Enforces the structure of the reuse-list (references/reuse-first.md「Reuse List
Format」) before implementation:

  * No reuse list / reuse-list at all → PASS (not-applicable).
  * Each row's evidence grade ∈ {Exact match, Similar pattern, Library exists,
    No match}.
  * Exact-match rows must carry a non-empty Source path AND a non-empty
    Capability checked.
  * No-match rows must carry a reason.
  * Any negative conclusion ("系统无 X / 未找到复用 / not found") must be backed
    by a Grep Evidence block — verified by reusing prd-to-spec's
    check_grep_evidence native-scan判定 (imported function, not re-implemented).

Presence-only: PASS proves the list is shaped right and negatives carry grep
evidence; it does NOT prove the reuse judgment (exact vs similar) is correct —
that goes to judge/人.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Reuse prd-to-spec/scripts/check_grep_evidence.py — import its functions
# instead of re-implementing the native ZERO_MATCH scan判定.
# --------------------------------------------------------------------------
def _load_grep_evidence_module():
    """Locate and import check_grep_evidence from the sibling prd-to-spec skill.

    Both skills live under the same skills root (~/.claude/skills or
    ~/.codex/skills, or a sandbox copy). This script sits at
    <root>/spec-to-code/scripts/, so prd-to-spec is ../../prd-to-spec.
    """
    here = Path(__file__).resolve()
    candidate = here.parents[2] / "prd-to-spec" / "scripts" / "check_grep_evidence.py"
    if not candidate.is_file():
        return None
    spec = importlib.util.spec_from_file_location("check_grep_evidence", candidate)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GREP_EVIDENCE = _load_grep_evidence_module()

# --------------------------------------------------------------------------
# Triggers and grammar
# --------------------------------------------------------------------------
REUSE_LIST_RE = re.compile(r"复用清单|reuse[\s\-]?list", re.IGNORECASE)

# Canonical evidence grades (references/reuse-first.md「Evidence Grades」).
GRADES = {
    "exact match": "Exact",
    "exact": "Exact",
    "精确命中": "Exact",
    "similar pattern": "Similar",
    "similar": "Similar",
    "类似": "Similar",
    "library exists": "Library",
    "library": "Library",
    "仅库存在": "Library",
    "库存在": "Library",
    "no match": "NoMatch",
    "no-match": "NoMatch",
    "未命中": "NoMatch",
    "无匹配": "NoMatch",
}

NEGATIVE_CONCLUSION_RE = re.compile(
    r"系统无|未找到复用|未找到|not\s+found|no\s+\w+\s+found|ZERO_MATCH",
    re.IGNORECASE,
)

EMPTY_CELL_RE = re.compile(r"^\s*(?:|[-—–]|n/?a|tbd|todo|无|待定|/)\s*$", re.IGNORECASE)


def split_cells(line: str) -> list[str]:
    parts = line.strip().strip("|").split("|")
    return [p.strip() for p in parts]


def is_separator(cells: list[str]) -> bool:
    joined = "".join(cells)
    return bool(joined) and set(joined) <= set("-: ")


def classify_grade(cell: str) -> str | None:
    low = cell.strip().lower()
    for key, norm in GRADES.items():
        if key in low:
            return norm
    return None


def parse_reuse_rows(text: str) -> tuple[list[dict], list[str]]:
    """Pull data rows out of the reuse list table.

    Returns (rows, header_cells). Each row dict: {cells, grade, lineno}. The
    grade column is detected by scanning each cell for a canonical grade word.
    """
    rows: list[dict] = []
    header: list[str] = []
    in_table = False
    grade_col: int | None = None

    lines = text.splitlines()
    for idx, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        cells = split_cells(stripped)
        if is_separator(cells):
            continue
        # Header row: contains "Evidence grade" / "证据档" / "evidence".
        joined_low = " ".join(cells).lower()
        if not in_table:
            if "grade" in joined_low or "证据" in joined_low or "evidence" in joined_low:
                header = cells
                grade_col = next(
                    (i for i, c in enumerate(cells)
                     if "grade" in c.lower() or "证据" in c or "evidence" in c.lower()),
                    None,
                )
                in_table = True
                continue
            # A table without a recognizable header — skip (not the reuse list).
            continue
        # Data row.
        grade = None
        if grade_col is not None and grade_col < len(cells):
            grade = classify_grade(cells[grade_col])
        if grade is None:
            grade = next((classify_grade(c) for c in cells if classify_grade(c)), None)
        rows.append({"cells": cells, "grade": grade, "lineno": idx, "header": header})
    return rows, header


def col_index(header: list[str], *needles: str) -> int | None:
    for i, c in enumerate(header):
        low = c.lower()
        if any(n in low for n in needles):
            return i
    return None


def cell_at(cells: list[str], idx: int | None) -> str:
    if idx is None or idx >= len(cells):
        return ""
    return cells[idx]


def check_rows(rows: list[dict]) -> list[str]:
    """Validate grade vocabulary + Exact/No-match column requirements."""
    fails: list[str] = []
    for row in rows:
        cells = row["cells"]
        header = row["header"]
        lineno = row["lineno"]
        grade = row["grade"]

        if grade is None:
            fails.append(
                f"第{lineno}行: 证据档不在 {{Exact match/Similar pattern/"
                f"Library exists/No match}} 之内: {cells!r}"
            )
            continue

        if grade == "Exact":
            src_idx = col_index(header, "source", "path", "源", "路径")
            cap_idx = col_index(header, "capability", "能力")
            src = cell_at(cells, src_idx)
            cap = cell_at(cells, cap_idx)
            if EMPTY_CELL_RE.match(src):
                fails.append(f"第{lineno}行 Exact-match 缺 Source 路径: {cells!r}")
            if EMPTY_CELL_RE.match(cap):
                fails.append(f"第{lineno}行 Exact-match 缺 Capability-checked: {cells!r}")

        if grade == "NoMatch":
            reason_idx = col_index(header, "reason", "理由", "adaptation", "wrapper", "原因")
            reason = cell_at(cells, reason_idx)
            if EMPTY_CELL_RE.match(reason):
                fails.append(f"第{lineno}行 No-match 缺理由: {cells!r}")
    return fails


def check_negative_conclusions(text: str, md_file: str) -> tuple[list[str], list[str]]:
    """Negative conclusions need a Grep Evidence block; verify via reuse.

    Returns (fails, infos). When the imported grep-evidence module is present we
    delegate row verification to it; otherwise we degrade to a structural check.
    """
    fails: list[str] = []
    infos: list[str] = []

    if not NEGATIVE_CONCLUSION_RE.search(text):
        return fails, infos

    has_block = "Grep Evidence" in text
    if not has_block:
        fails.append("否定结论(系统无X/未找到复用)缺 Grep Evidence 块")
        return fails, infos

    if GREP_EVIDENCE is None:
        infos.append(
            "WARN: 未能 import check_grep_evidence(prd-to-spec 不在同级 skills 根),"
            "仅做结构检查"
        )
        # Structural fallback: required columns must be present.
        missing = [c for c in ("Claim", "Wordset", "Command", "Hits", "Conclusion")
                   if c not in text]
        if missing:
            fails.append("Grep Evidence 块缺列: " + ", ".join(missing))
        return fails, infos

    # Delegate to the imported native-scan verifier.
    rows = GREP_EVIDENCE.parse_evidence_rows(text)
    if not rows:
        infos.append("Grep Evidence 块在场但无可验数据行(结构兜底通过)")
        return fails, infos
    repo, repo_err = GREP_EVIDENCE.resolve_repo(None)
    if repo is None:
        infos.append(f"WARN: 无法解析 repo({repo_err}),grep 证据仅结构在场")
        return fails, infos
    g_fails, g_warns, g_oks = GREP_EVIDENCE.verify_rows(rows, repo)
    for m in g_oks:
        infos.append(m)
    for m in g_warns:
        infos.append("WARN: " + m)
    fails.extend(g_fails)
    return fails, infos


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_reuse_first.py <markdown-file>", file=sys.stderr)
        return 2

    md_file = sys.argv[1]
    text = Path(md_file).read_text(encoding="utf-8")

    if not REUSE_LIST_RE.search(text):
        print("PASS: reuse-first check not applicable (no 复用清单/reuse-list)")
        print("(presence-only:无复用清单;复用判断对否交judge/人)")
        return 0

    rows, _ = parse_reuse_rows(text)
    if not rows:
        # The trigger word appears (e.g. in prose) but no actual reuse-list table
        # was parsed — there is nothing to validate. Treat as not-applicable
        # rather than green-washing a non-existent list.
        print("PASS: reuse-first check not applicable (提及复用清单但无可解析的清单表)")
        print("(presence-only:无可解析复用清单;复用判断对否交judge/人)")
        return 0

    row_fails = check_rows(rows)
    neg_fails, neg_infos = check_negative_conclusions(text, md_file)

    for info in neg_infos:
        print(info if info.startswith("WARN") else "  " + info)

    fails = row_fails + neg_fails
    if fails:
        print("FAIL: 复用清单/否定结论结构不合规:")
        for f in fails:
            print("  - " + f)
        return 1

    print(f"PASS: 复用清单结构合规({len(rows)} 行,证据档/Exact源/No-match理由齐备)")
    print("(presence-only:结构合规,Exact是否真精确/复用判断对否交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
