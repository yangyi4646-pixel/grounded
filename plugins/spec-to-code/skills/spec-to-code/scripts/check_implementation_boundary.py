#!/usr/bin/env python3
"""Implementation-boundary check: structure presence + changed-file reconciliation.

Structure (presence) layer — unchanged from batch A:
  - Implementation Boundary heading present.
  - Required columns present (Allowed Targets / Forbidden Targets / Propagation Rule / SPEC Source).
Reconciliation layer (batch D):
  - Parse Allowed / Forbidden glob patterns from the boundary table.
  - Collect changed files (git diff HEAD by default; --base <ref>; --changed-files-from <file>).
  - Every changed file must match >=1 Allowed glob and 0 Forbidden globs, else FAIL.
  - Graceful degradation: no git / no changes / no boundary table -> WARN + PASS (STRUCTURE-ONLY).
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

REQUIRED = [
    "Allowed Targets",
    "Forbidden Targets",
    "Propagation Rule",
    "SPEC Source",
]

BOUNDARY_HEADING = re.compile(
    r"^##?#?\s*Implementation Boundary\b|Implementation boundary table",
    re.MULTILINE | re.IGNORECASE,
)

# Pattern-ish cell tokens: keep things that look like a path/glob, drop prose.
_PATTERN_TOKEN = re.compile(r"[A-Za-z0-9_./*?\[\]{}~-]+")
# Placeholder/prose tokens that are never real targets.
_PLACEHOLDER = {"", "-", "--", "n/a", "na", "none", "tbd", "todo", "无", "待定"}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="check_implementation_boundary.py",
        description="Check implementation-boundary structure and reconcile changed files.",
    )
    parser.add_argument("markdown_file", help="boundary markdown file (SPEC / boundary table)")
    parser.add_argument(
        "--base",
        metavar="REF",
        default=None,
        help="reconcile changes against this git ref (git diff --name-only <REF>); "
        "default reconciles uncommitted changes via 'git diff --name-only HEAD'",
    )
    parser.add_argument(
        "--changed-files-from",
        metavar="FILE",
        dest="changed_files_from",
        default=None,
        help="read changed-file list from FILE (one path per line); "
        "bypasses git entirely — use for regression tests",
    )
    parser.add_argument(
        "--repo-root",
        metavar="DIR",
        default=None,
        help="repo root for normalizing changed paths (default: git toplevel, else cwd)",
    )
    return parser.parse_args(argv)


# --- glob extraction ---------------------------------------------------------

def _split_cells(line: str) -> list[str]:
    """Split a markdown table row into trimmed cells (drop leading/trailing pipe edges)."""
    raw = line.strip()
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|"):
        raw = raw[:-1]
    return [c.strip() for c in raw.split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c) and any(cells)


def _extract_patterns(cell: str) -> list[str]:
    """Pull glob/path-looking tokens out of a table cell, dropping prose/placeholders."""
    out: list[str] = []
    for tok in _PATTERN_TOKEN.findall(cell):
        cleaned = tok.strip("`").strip()
        if cleaned.lower() in _PLACEHOLDER:
            continue
        # Require it to look like a path or glob: contains a slash, glob metachar, or dot-ext.
        if "/" in cleaned or "*" in cleaned or "?" in cleaned or "[" in cleaned:
            out.append(cleaned)
        elif re.search(r"\.[A-Za-z0-9]+$", cleaned):  # bare filename like foo.test.ts
            out.append(cleaned)
    return out


def extract_globs(text: str) -> tuple[list[str], list[str], bool]:
    """Return (allowed_globs, forbidden_globs, table_found).

    Parses the boundary table: locates the header row containing Allowed/Forbidden
    columns, then reads every following data row until the table ends.
    """
    lines = text.splitlines()
    header_idx = None
    allowed_col = forbidden_col = None
    for i, line in enumerate(lines):
        if "|" not in line:
            continue
        cells = _split_cells(line)
        lowered = [c.lower() for c in cells]
        if "allowed targets" in lowered and "forbidden targets" in lowered:
            header_idx = i
            allowed_col = lowered.index("allowed targets")
            forbidden_col = lowered.index("forbidden targets")
            break
    if header_idx is None:
        return [], [], False

    allowed: list[str] = []
    forbidden: list[str] = []
    for line in lines[header_idx + 1:]:
        if "|" not in line:
            if line.strip() == "":
                break  # blank line ends the table
            continue
        cells = _split_cells(line)
        if _is_separator_row(cells):
            continue
        if allowed_col < len(cells):
            allowed.extend(_extract_patterns(cells[allowed_col]))
        if forbidden_col < len(cells):
            forbidden.extend(_extract_patterns(cells[forbidden_col]))
    return _dedup(allowed), _dedup(forbidden), True


def _dedup(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out


# --- glob matching (with ** recursion) ---------------------------------------

def _normalize(path: str) -> str:
    """Normalize to posix, strip leading ./ and / so patterns anchor at repo root."""
    p = path.strip().replace("\\", "/")
    p = re.sub(r"^\./+", "", p)
    p = p.lstrip("/")
    return p


def glob_match(path: str, pattern: str) -> bool:
    """Match path against a glob supporting ** (recursive across /) and * (single segment).

    A bare filename pattern (no slash) matches any basename in the tree; a pattern
    ending in / is treated as a recursive directory prefix.
    """
    path = _normalize(path)
    pat = _normalize(pattern)
    if not pat:
        return False

    # Bare filename glob (no slash): match the basename anywhere in the tree.
    if "/" not in pat:
        return fnmatch.fnmatchcase(PurePosixPath(path).name, pat)

    # Directory prefix shorthand: "foo/bar/" -> "foo/bar/**".
    if pat.endswith("/"):
        pat = pat + "**"

    regex = _glob_to_regex(pat)
    return regex.fullmatch(path) is not None


def _glob_to_regex(pat: str) -> re.Pattern[str]:
    """Translate a glob with ** into an anchored regex. ** spans /, * does not."""
    i = 0
    n = len(pat)
    out: list[str] = []
    while i < n:
        c = pat[i]
        if c == "*":
            if i + 1 < n and pat[i + 1] == "*":
                # consume a run of * (treat *** as **)
                j = i
                while j < n and pat[j] == "*":
                    j += 1
                # '**/' -> zero or more leading segments; trailing '**' -> anything
                if j < n and pat[j] == "/":
                    out.append(r"(?:.*/)?")
                    i = j + 1
                else:
                    out.append(r".*")
                    i = j
            else:
                out.append(r"[^/]*")
                i += 1
        elif c == "?":
            out.append(r"[^/]")
            i += 1
        elif c == "[":
            j = i + 1
            if j < n and pat[j] in "!^":
                j += 1
            if j < n and pat[j] == "]":
                j += 1
            while j < n and pat[j] != "]":
                j += 1
            if j >= n:
                out.append(re.escape("["))  # unterminated class -> literal
                i += 1
            else:
                cls = pat[i + 1:j]
                if cls.startswith(("!", "^")):
                    cls = "^" + cls[1:]
                out.append("[" + cls + "]")
                i = j + 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile("".join(out))


# --- changed-file collection -------------------------------------------------

def _git_toplevel() -> str | None:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False,
        )
    except (OSError, FileNotFoundError):
        return None
    if res.returncode != 0:
        return None
    top = res.stdout.strip()
    return top or None


def _git_changed(base: str | None) -> tuple[list[str] | None, str | None]:
    """Return (files, error). files=None means git unavailable / not a repo / bad ref."""
    # Disambiguate not-a-repo from bad-ref so the WARN reason is clean.
    if _git_toplevel() is None:
        return None, "不在 git 仓库（或 git 不可用）"
    ref = base if base else "HEAD"
    try:
        res = subprocess.run(
            ["git", "diff", "--name-only", ref],
            capture_output=True, text=True, check=False,
        )
    except (OSError, FileNotFoundError):
        return None, "git 不可用"
    if res.returncode != 0:
        return None, f"git ref 无效或 diff 失败: {ref}"
    files = [ln.strip() for ln in res.stdout.splitlines() if ln.strip()]
    return files, None


def _read_changed_file(path: str) -> tuple[list[str] | None, str | None]:
    p = Path(path)
    if not p.exists():
        return None, f"--changed-files-from 文件不存在: {path}"
    try:
        content = p.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"无法读取 --changed-files-from: {exc}"
    files = [
        ln.strip()
        for ln in content.splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]
    return files, None


def collect_changed(args: argparse.Namespace) -> tuple[list[str] | None, str | None, str | None]:
    """Return (changed_files, repo_root, degrade_reason).

    changed_files=None with a degrade_reason -> structure-only fallback.
    """
    if args.changed_files_from:
        files, err = _read_changed_file(args.changed_files_from)
        if err:
            return None, None, err
        root = args.repo_root or _git_toplevel() or "."
        return files, root, None

    files, err = _git_changed(args.base)
    if files is None:
        return None, None, err
    root = args.repo_root or _git_toplevel() or "."
    return files, root, None


def _rel_to_root(path: str, root: str) -> str:
    """Make an absolute changed path relative to repo root; leave relative paths as-is."""
    p = Path(path)
    if p.is_absolute() and root not in (None, "", "."):
        try:
            return str(p.relative_to(Path(root)))
        except ValueError:
            return _normalize(path)
    return _normalize(path)


# --- reconciliation ----------------------------------------------------------

def reconcile(
    changed: list[str], root: str, allowed: list[str], forbidden: list[str]
) -> tuple[bool, list[str]]:
    """Return (ok, violations). violations is a list of human-readable failure lines."""
    violations: list[str] = []
    for raw in changed:
        rel = _rel_to_root(raw, root)
        hit_forbidden = [pat for pat in forbidden if glob_match(rel, pat)]
        if hit_forbidden:
            violations.append(f"  - {rel} 命中 Forbidden: {', '.join(hit_forbidden)}")
            continue
        if not any(glob_match(rel, pat) for pat in allowed):
            violations.append(f"  - {rel} 越出 Allowed 范围（未匹配任何 Allowed 模式）")
    return (len(violations) == 0), violations


# --- presence + main ---------------------------------------------------------

def check_presence(text: str) -> str | None:
    """Return a FAIL message if structure is missing, else None."""
    if not BOUNDARY_HEADING.search(text):
        return "FAIL: missing Implementation Boundary"
    missing = [name for name in REQUIRED if name not in text]
    if missing:
        return "FAIL: missing columns: " + ", ".join(missing)
    return None


def _print_structure_only(reason: str) -> int:
    print("WARN: 未能对账:" + reason)
    print("PASS (STRUCTURE-ONLY): implementation boundary structure present")
    print("(presence-only:结构合规,越界真值未对账,模式语义/范围划得对否交judge/人)")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    md_path = Path(args.markdown_file)
    if not md_path.exists():
        print(f"FAIL: markdown file not found: {args.markdown_file}", file=sys.stderr)
        return 2
    text = md_path.read_text(encoding="utf-8")

    # 1) Presence layer (unchanged): missing table/columns still FAIL.
    fail = check_presence(text)
    if fail:
        print(fail)
        return 1

    # 2) Reconciliation layer.
    allowed, forbidden, table_found = extract_globs(text)
    if not table_found or not allowed:
        return _print_structure_only(
            "Boundary 表无可解析的 Allowed 模式" if table_found else "未找到 Boundary 表行"
        )

    changed, root, degrade = collect_changed(args)
    if degrade is not None:
        return _print_structure_only(degrade)
    if changed is not None and len(changed) == 0:
        return _print_structure_only("无改动文件可对账")

    ok, violations = reconcile(changed, root or ".", allowed, forbidden)
    if not ok:
        print("FAIL: changed files violate implementation boundary")
        for line in violations:
            print(line)
        return 1

    print(f"PASS: {len(changed)} changed file(s) reconciled against implementation boundary")
    print("(越界已对账;模式语义/范围划得对否交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
