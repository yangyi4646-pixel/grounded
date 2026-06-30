#!/usr/bin/env python3
"""N2 · Capability-verification presence check (presence-only).

Door C in the protocol (§4.2): before升级 a symbol to「精确命中 / 可直接复用 /
exact match」, the author must have read the implementation and left a verifiable
evidence line near the claim, in the prescribed shape, e.g.:

  精确命中? 符号 MetricBatchOperate | 读实现: batchActions=[del, move] | \
  含目标动作? 否 | 结论: 类似能力,不可复用

Door triggers only on a *real reuse assertion* — a 精确命中 / 可直接复用 /
exact match line that ALSO names a concrete symbol on the same line (a
CamelCase/PascalCase identifier, a path with /, a .tsx-style extension, or a
file:line ref). A real reuse assertion always names the thing being reused
(MetricBatchOperate / TooltipIcon / MetricVersionHistory). A line that only
discusses the *concept* ("精确命中前必读实现", "类似能力→精确命中越级", a protocol
rubric row) names no symbol and is NOT a reuse assertion — it must not be forced
to carry an evidence line. This kills the误伤 on concept-discussion docs.

Behavior:
  * No triggering claim (vocabulary absent, OR present only in concept
    discussion with no named symbol) → PASS (not-applicable).
  * Triggering claim present → for EACH such claim there must be a nearby
    evidence line carrying the required fields (读实现 + 含目标动作? + 结论).
    Missing → FAIL listing the naked claim.

This is presence-only: it proves an evidence line is present and shaped right,
NOT that the read-implementation result is true. The semantic "does this symbol
really do that?" check is judge/人 territory (protocol door C, depends on the
地基门).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Lines that assert an exact-capability reuse claim.
CLAIM_RE = re.compile(r"精确命中|可直接复用|exact\s*match", re.IGNORECASE)

# A claim only requires nearby evidence when the SAME line also names a concrete
# symbol — i.e. it is asserting reuse OF something specific. A real reuse
# assertion always names the reused symbol (MetricBatchOperate / TooltipIcon /
# MetricVersionHistory). A line that merely discusses the *concept* ("精确命中前
# 必读实现", "类似能力→精确命中越级", a protocol rubric row) names no symbol and
# is NOT a reuse assertion, so it must not be forced to carry an evidence line.
# Symbol classes that count as "names a concrete symbol". ALL are ASCII-anchored
# on purpose: \w in Python matches CJK, so a Chinese concept enumeration like
# "类似能力/可直接复用" would otherwise be misread as a slash-path. A real reused
# symbol is an ASCII identifier / path / file ref, never a Chinese phrase.
_ID = r"[A-Za-z_][A-Za-z0-9_]*"  # ASCII identifier
SYMBOL_RES: list[re.Pattern[str]] = [
    # Camel/PascalCase identifier: a mixed-case ASCII run with an internal
    # capital boundary AND at least one lowercase letter — e.g.
    # MetricBatchOperate, TooltipIcon, batchActions, IMetricStatus. The
    # mandatory lowercase letter (enforced by the (?=...) lookahead) is what
    # makes it a *real* code identifier rather than an all-caps acronym: a bare
    # acronym like LLM / API / BI / SPEC / RECON / AC1 has no lowercase letter
    # and so must NOT be read as a named symbol — otherwise it false-triggers
    # the evidence door on pure concept-discussion prose, e.g.
    # "纯 prose + LLM-judge" or "对抗 LLM-judge 实读代码". The base shape
    # (internal-capital run) is unchanged from the original; only the lowercase
    # lookahead is added, so interface/Pascal symbols like IMetricStatus or
    # DCTree (which DO contain a lowercase letter) still count.
    re.compile(r"\b(?=[A-Za-z0-9]*[a-z])[A-Za-z][a-z0-9]*[A-Z][A-Za-z0-9]*\b"),
    # ASCII path: src/app/..., src/foo/bar, page-manager.ts paths. Must
    # look path-shaped — either ≥2 slashes (a/b/c) or a dotted segment
    # (foo/bar.ts) — so a bare "N/A" or a two-word "X/Y" abbreviation is NOT
    # read as a path. (中文/中文 is already excluded by the ASCII char classes.)
    re.compile(
        r"[A-Za-z0-9._\-]+/[A-Za-z0-9._\-]+/[A-Za-z0-9._/\-]+"  # ≥2 slashes
        r"|[A-Za-z0-9_\-]+/[A-Za-z0-9_\-]*\.[A-Za-z0-9._/\-]+"  # dotted file
    ),
    # Source-file extension on an ASCII basename.
    re.compile(r"\b[A-Za-z0-9_\-]+\.(?:tsx|ts|jsx|js|py|scss|css|json)\b"),
    # file:line reference, e.g. page-manager.ts:100 or foo:42.
    re.compile(r"\b" + _ID + r"[A-Za-z0-9._/\-]*:\d+\b"),
]


def names_concrete_symbol(line: str) -> bool:
    """True if the line points at a specific symbol/path/file:line.

    This distinguishes a real reuse assertion (names what is being reused) from
    pure concept discussion of the 精确命中/可直接复用 vocabulary.
    """
    return any(pat.search(line) for pat in SYMBOL_RES)


# An evidence line must carry the read-implementation marker AND the
#含目标动作? gate AND a 结论. We check the三件套 are co-present on (or very
# near) the same line. The协议蓝本 shape:
#   "精确命中? 符号X | 读实现: … | 含目标动作? 是/否 | 结论: …"
EVID_READ_RE = re.compile(r"读实现\s*[:：]|read[\s\-]?impl", re.IGNORECASE)
EVID_ACTION_RE = re.compile(r"含目标动作\s*[?？]|has[\s\-]?target[\s\-]?action", re.IGNORECASE)
EVID_CONCLUSION_RE = re.compile(r"结论\s*[:：]|conclusion\s*[:：]", re.IGNORECASE)

# How many lines around a claim count as "nearby" for the evidence line.
NEARBY_WINDOW = 2


def is_evidence_line(line: str) -> bool:
    """An evidence line carries read-impl + target-action gate + conclusion."""
    return bool(
        EVID_READ_RE.search(line)
        and EVID_ACTION_RE.search(line)
        and EVID_CONCLUSION_RE.search(line)
    )


def has_nearby_evidence(lines: list[str], claim_idx: int) -> bool:
    """True if an evidence line sits on or within NEARBY_WINDOW of the claim.

    The claim line itself often IS the evidence line (single-row format), so we
    include it in the window.
    """
    lo = max(0, claim_idx - NEARBY_WINDOW)
    hi = min(len(lines), claim_idx + NEARBY_WINDOW + 1)
    return any(is_evidence_line(lines[i]) for i in range(lo, hi))


def triggering_claim_lines(text: str) -> list[int]:
    """Indices of lines that are real reuse assertions (claim + named symbol).

    A concept-discussion line carrying the 精确命中/可直接复用 vocabulary but no
    concrete symbol is NOT a triggering claim — the evidence door is off for it.
    """
    return [
        idx
        for idx, line in enumerate(text.splitlines())
        if CLAIM_RE.search(line) and names_concrete_symbol(line)
    ]


def find_naked_claims(text: str) -> list[tuple[int, str]]:
    """Return (lineno, line) for each triggering claim lacking nearby evidence."""
    lines = text.splitlines()
    naked: list[tuple[int, str]] = []
    for idx in triggering_claim_lines(text):
        # A claim line that is itself a complete evidence line is satisfied.
        if has_nearby_evidence(lines, idx):
            continue
        naked.append((idx + 1, lines[idx].strip()))
    return naked


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_capability_verification.py <markdown-file>", file=sys.stderr)
        return 2

    text = Path(sys.argv[1]).read_text(encoding="utf-8")

    # Door triggers only on a real reuse assertion: a 精确命中/可直接复用 line
    # that also names a concrete symbol. No such line (whether the vocabulary is
    # absent entirely, or only appears in concept discussion) → not-applicable.
    if not triggering_claim_lines(text):
        print("PASS: capability-verification check not applicable (no 精确命中/可直接复用 claim)")
        print("(presence-only:无点名符号的复用断言;能力核验真假交judge/人)")
        return 0

    naked = find_naked_claims(text)
    if naked:
        print("FAIL: 精确命中/可直接复用 claim 缺邻近读实现证据行:")
        for lineno, line in naked:
            shown = line[:90]
            print(f"  - 第{lineno}行: {shown!r}")
        print(
            "  需邻近一行带: 读实现: … | 含目标动作? 是/否 | 结论: …"
        )
        return 1

    print("PASS: 每条精确命中/可直接复用 claim 均带读实现证据行")
    print("(presence-only:结构合规,符号真含目标能力否交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
