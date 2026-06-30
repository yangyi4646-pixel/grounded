#!/usr/bin/env python3
"""N1 · C2 user-section jargon check (presence-only).

Extracts the 【给用户】 … 【内部留痕】 segment and scans it for
"implementation symbol" tokens. The 【给用户】 segment is what a non-expert
user must be able to answer, so it must be pure business language — no paths,
file extensions, identifiers, API dot-chains, line/section refs, or backtick
code spans.

Behavior:
  * No 【给用户】 *segment opener* → PASS (not-applicable): nothing to scan.
    【给用户】 only opens a segment when it sits at line head as a separator
    (after optional #/##/>/list-bullet/whitespace). A mid-sentence mention —
    e.g. a meta-doc prose line "把问题落在【给用户】段" — is NOT a segment and
    is never scanned (structural anchoring; avoids the误伤 where a doc merely
    talks about the marker).
  * 【给用户】 segment present → scan only that segment, which ends at the next
    【内部留痕】 line OR the next section heading, whichever comes first (never
    bleeds into 【内部留痕】). Any token class hit → FAIL, reporting the
    offending token + line.

The token regex blueprint is reused from
tests/quality-test-protocol.md (C2 §4.1 user-section regex + §4 grounding
template). A small whitelist of business-common acronyms (BI/ETL/SQL/...) is
kept inline; it is maintained by prose, not by this script — see WHITELIST note.

PASS here is presence-only: it proves the user segment is symbol-clean, not that
the questions are well-framed business questions. That judgment goes to judge/人.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Segment markers.
USER_MARK = "【给用户】"
INTERNAL_MARK = "【内部留痕】"

# Structural anchor: 【给用户】 only opens a user segment when it acts as a
# section separator, i.e. one of:
#   (a) a Markdown heading line carrying the marker, e.g. "## 四、确认门【给用户】"
#       (line starts with #, marker anywhere on that heading line); or
#   (b) the marker at true line-head, optionally after whitespace / a list
#       bullet (-/*/+) / a blockquote (>) — e.g. a bare "【给用户】" on its own
#       line above the question list.
# A mid-sentence mention in *body prose* — e.g. findings.md's
# "把问题落在【给用户】段" or "对【给用户】段" — is NOT a separator: the marker is
# preceded by non-whitespace body text on a non-heading line. We must not treat
# the rest of the doc as a user segment there. This kills the false positive
# where a meta-doc merely *talks about* 【给用户】.
HEADING_LINE = re.compile(r"^[ \t]*#")
USER_MARK_AT_LINE_HEAD = re.compile(
    r"^[ \t]*(?:>[ \t]*|[-*+][ \t]*)*" + re.escape(USER_MARK)
)
# The user segment ends at the next 【内部留痕】 OR the next section heading
# (a line beginning with one or more # at line-head), whichever comes first.
NEXT_HEADING = re.compile(r"^[ \t]*#+[ \t]")


def is_segment_opener(line: str) -> bool:
    """True if this line opens a 【给用户】 user segment (structural separator)."""
    if USER_MARK not in line:
        return False
    # (a) heading line carrying the marker.
    if HEADING_LINE.match(line):
        return True
    # (b) marker at true line-head (after whitespace / bullet / blockquote).
    return bool(USER_MARK_AT_LINE_HEAD.match(line))


# --- Whitelist (prose-maintained) -----------------------------------------
# Business-common acronyms that are legitimate domain vocabulary, NOT
# implementation jargon. This list is intentionally small and is maintained by
# a human editing this file (prose), not auto-derived. Adding a term here is a
# product-vocabulary decision. The §4.1 protocol note: "允许少量业务域词(如
# BI)不计入;API、ID、URL 默认不放行" — so API/ID/URL stay OUT of the
# whitelist on purpose.
WHITELIST = {
    "BI", "ETL", "SQL", "KPI", "OKR", "SaaS", "UV", "PV", "GMV", "ROI",
    "CRM", "ERP", "OLAP", "BOM", "SKU",
}

# --- Implementation-symbol token classes (blueprint from protocol §4.1) ----
# Each class is its own pattern so a hit can be reported with a class label.
TOKEN_CLASSES: list[tuple[str, re.Pattern[str]]] = [
    # Path with a slash: packages/, src/, /api/, foo/bar
    ("path-with-slash", re.compile(r"\b[\w.\-]+/[\w./\-]+")),
    # Source-file extensions.
    ("file-ext", re.compile(r"\b[\w\-]+\.(?:tsx|ts|jsx|js|py|scss|css|json)\b")),
    # camelCase identifier (a lower run, an internal capital, more chars).
    ("camelCase", re.compile(r"\b[a-z]+[a-z0-9]*[A-Z][A-Za-z0-9]*\b")),
    # SCREAMING_SNAKE_CASE constant.
    ("SCREAMING_SNAKE", re.compile(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b")),
    # Dotted API / member chain, e.g. a.b.c() or INFO_MAP.field.
    ("api-dot-chain", re.compile(r"\b[A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*){1,}(?:\s*\()?")),
    # Line ref :123 or section ref §4.
    ("line/section-ref", re.compile(r":\d+\b|§\s*\d+")),
    # Backtick code span.
    ("backtick-code-span", re.compile(r"`[^`]+`")),
    # Process meta-talk that leaks the harness/flow into the user segment.
    ("process-meta", re.compile(r"AskUserQuestion|降级\s*rule|无交互降级|占位")),
]


def extract_user_segment(text: str) -> str | None:
    """Return the 【给用户】 user segment, or None if no segment-opener marker.

    Structure-anchored: 【给用户】 only opens a segment when it appears at line
    head as a section separator (after optional #/##/>/list-bullet/whitespace).
    A mid-sentence mention is ignored. The segment runs from the line AFTER the
    opener to (exclusive) the first of: a 【内部留痕】 line, the next section
    heading, or EOF. Returns the segment body text (markers stripped).
    """
    lines = text.splitlines()
    open_idx = None
    for idx, line in enumerate(lines):
        if is_segment_opener(line):
            open_idx = idx
            break
    if open_idx is None:
        return None

    # Body starts after the opener line. Anything on the opener line after the
    # marker itself (e.g. "## 四、确认门【给用户】" has nothing; a bare
    # "【给用户】" likewise) is heading text, not user content, so we begin at
    # the next line.
    seg_lines: list[str] = []
    for line in lines[open_idx + 1:]:
        if INTERNAL_MARK in line or NEXT_HEADING.match(line):
            break
        seg_lines.append(line)
    return "\n".join(seg_lines)


def whitelisted(token: str) -> bool:
    """True if the whole token (case-insensitive) is a whitelisted acronym."""
    return token.strip().upper() in {w.upper() for w in WHITELIST}


def scan_segment(segment: str) -> list[tuple[int, str, str]]:
    """Scan the user segment line by line.

    Returns a list of (lineno, token_class, token) hits. Whitelisted bare
    acronyms are skipped. Line numbers are 1-based within the segment.
    """
    hits: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(segment.splitlines(), 1):
        for label, pat in TOKEN_CLASSES:
            for m in pat.finditer(line):
                token = m.group(0).strip()
                if not token:
                    continue
                # A bare whitelisted acronym (e.g. "BI") is allowed. This only
                # rescues the SCREAMING_SNAKE / dotted-chain classes when the
                # entire matched token is itself the acronym.
                if whitelisted(token):
                    continue
                hits.append((lineno, label, token))
    return hits


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_c2_user_section.py <markdown-file>", file=sys.stderr)
        return 2

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    segment = extract_user_segment(text)

    if segment is None:
        print("PASS: C2 user-section check not applicable (no 【给用户】 marker)")
        print("(presence-only:无用户段可扫;问题是否纯业务语义交judge/人)")
        return 0

    hits = scan_segment(segment)
    if hits:
        print("FAIL: 【给用户】段出现实现符号 token(应为纯业务语义):")
        for lineno, label, token in hits:
            print(f"  - 段内第{lineno}行 [{label}] -> {token!r}")
        print("白名单(prose 维护): " + ", ".join(sorted(WHITELIST)))
        return 1

    print("PASS: 【给用户】段无实现符号 token")
    print("(presence-only:结构合规,问题是否纯业务语义/可答交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
