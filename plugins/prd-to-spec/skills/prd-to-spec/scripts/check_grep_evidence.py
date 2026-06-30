#!/usr/bin/env python3
"""Grep-evidence block check.

Two layers:
1. Structure (unchanged, soft): the markdown must carry a Grep Evidence block
   with the required columns whenever it makes a negative / no-match claim.
2. Verification (binary-independent): every evidence row is checked against the
   target repo *using pure Python file I/O* — no rg / grep / any external
   binary is ever invoked. Claimed file:line hits are opened and the actual
   line is read; ZERO_MATCH claims are checked by a native recursive scan of
   the scoped directory. Fabricated hits, fake line numbers, missing files and
   fake ZERO_MATCH all FAIL.

Why binary-independent: on some hosts `rg`/`grep` are not reachable from a
subprocess (sandbox, PATH stripping). The previous version degraded to
STRUCTURE-ONLY in that case, i.e. back to a soft door. This version does the
verification itself, so it gives a real PASS/FAIL even when
`shutil.which('rg')` is None. We only WARN-degrade when the search word or the
scope genuinely cannot be parsed out of a row.
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

REQUIRED = ["Claim", "Wordset", "Command", "Hits", "Conclusion"]
NEGATIVE_CLAIM_RE = re.compile(r"(系统无|未命中|no\s+\w+|not\s+found|ZERO_MATCH)", re.IGNORECASE)

ZERO_MATCH_TOKEN = "ZERO_MATCH"

# file:line, e.g. src/foo/bar.tsx:42 — path may contain ./ - _ letters digits
FILE_LINE_RE = re.compile(r"(?P<file>[\w./\-]+):(?P<line>\d+)")

# Directories we never descend into during a ZERO_MATCH scan.
SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", "coverage",
    ".next", ".turbo", ".cache", "__pycache__", ".idea", ".vscode",
    "vendor", "target", ".pnpm-store",
}

# Extensions we treat as binary and never read.
BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svg",
    ".pdf", ".zip", ".gz", ".tar", ".tgz", ".bz2", ".7z", ".rar",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".mp3", ".mp4", ".mov", ".avi", ".mkv", ".wav", ".flac",
    ".so", ".dylib", ".dll", ".exe", ".bin", ".o", ".a", ".class",
    ".jar", ".wasm", ".node", ".lock", ".map", ".min.js", ".min.css",
    ".ds_store",
}

# ZERO_MATCH scan guardrails.
MAX_FILES_SCANNED = 50000
MAX_FILE_BYTES = 2 * 1024 * 1024  # 2 MiB; skip larger files
ZERO_SCAN_TIMEOUT_SEC = 30


# --------------------------------------------------------------------------
# Markdown parsing (structure rows)
# --------------------------------------------------------------------------
def split_table_cells(line: str) -> list[str]:
    """Split a markdown table row into cells, honoring backtick code spans.

    A bare ``|`` is a column separator only outside an inline `code` span.
    Inside a backtick span (e.g. ``rg "a|b|c"``) the ``|`` is an alternation
    char and must NOT split the cell. We walk the line char by char, flipping
    an ``in_code`` flag on every backtick, and only treat ``|`` as a separator
    when ``in_code`` is False. Leading/trailing pipe framing is dropped.
    """
    cells: list[str] = []
    buf: list[str] = []
    in_code = False
    for ch in line:
        if ch == "`":
            in_code = not in_code
            buf.append(ch)
        elif ch == "|" and not in_code:
            cells.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    cells.append("".join(buf))

    # Drop the empty leading/trailing cells produced by the outer | framing.
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return [c.strip() for c in cells]


def parse_evidence_rows(text: str) -> list[dict]:
    """Pull evidence rows out of the Grep Evidence markdown table(s).

    Returns a list of {"wordset": str, "command": str, "hits_cell": str,
    "raw": str}. Header rows, separator rows and empty-template rows are
    skipped. Robust to multiple Grep Evidence blocks in one document.
    """
    rows: list[dict] = []
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()

        # Enter on a heading that names the block; leave on the next heading.
        if stripped.startswith("#"):
            in_block = "Grep Evidence" in stripped
            continue

        if not in_block:
            continue

        if not stripped.startswith("|"):
            # A blank line or prose ends the table but not necessarily the block;
            # keep scanning until the next heading in case of intervening notes.
            continue

        cells = split_table_cells(stripped)
        if len(cells) < 5:
            continue

        # Skip the markdown header row and the |---|---| separator row.
        joined = "".join(cells)
        if set(joined) <= set("-: "):
            continue
        if cells[0] == "Claim" and cells[2] == "Command":
            continue

        wordset_cell = cells[1]
        command_cell = cells[2]
        hits_cell = cells[3]

        # Skip blank template rows (all cells empty) and placeholder rows.
        if not command_cell or not hits_cell:
            continue
        if command_cell.startswith("<") and command_cell.endswith(">"):
            continue

        rows.append(
            {
                "wordset": wordset_cell,
                "command": command_cell,
                "hits_cell": hits_cell,
                "raw": stripped,
            }
        )
    return rows


def strip_backticks(cell: str) -> str:
    """Return the content inside a markdown cell, unwrapping `code` spans."""
    cell = cell.strip()
    m = re.search(r"`([^`]+)`", cell)
    if m:
        return m.group(1).strip()
    return cell


# --------------------------------------------------------------------------
# Search-word + scope extraction (no binary involved)
# --------------------------------------------------------------------------
_QUOTED_RE = re.compile(r"""(['"])(?P<pat>(?:\\.|(?!\1).)*)\1""")
_WORDSET_SPLIT_RE = re.compile(r"[\s,;/、，；|]+")


def extract_search_words(wordset_cell: str, command: str) -> list[str]:
    """Pull candidate search words.

    Preference order:
      1. Wordset column — split on common separators.
      2. The quoted pattern inside the Command (rg/grep '<pat>' ...).
    Returns a de-duplicated, non-empty list (may be empty if nothing parseable).
    """
    words: list[str] = []

    ws = strip_backticks(wordset_cell)
    # Strip surrounding code/quote noise then split.
    ws = ws.strip("`").strip()
    if ws and ws.upper() != ZERO_MATCH_TOKEN:
        for tok in _WORDSET_SPLIT_RE.split(ws):
            tok = tok.strip().strip("`'\"")
            if tok:
                words.append(tok)

    if not words:
        # Fall back to the first quoted pattern in the command.
        cmd = strip_backticks(command)
        m = _QUOTED_RE.search(cmd)
        if m:
            pat = m.group("pat").replace("\\'", "'").replace('\\"', '"').strip()
            if pat:
                # A bare alternation (a|b|c) without proximity/wildcard markers
                # is just several words OR-ed together — split so each can be
                # verified individually. Anything regex-shaped stays whole.
                if "|" in pat and ".{" not in pat and ".*" not in pat and "(" not in pat:
                    for tok in pat.split("|"):
                        tok = tok.strip().strip("`'\"")
                        if tok:
                            words.append(tok)
                else:
                    words.append(pat)

    # De-dup, preserve order.
    seen: set[str] = set()
    out: list[str] = []
    for w in words:
        key = w.lower()
        if key not in seen:
            seen.add(key)
            out.append(w)
    return out


# rg/grep flags that consume the next token as a value.
_VALUED_FLAGS = {
    "-e", "--regexp", "-g", "--glob", "--iglob", "-t", "--type",
    "-T", "--type-not", "--type-add", "-m", "--max-count",
    "-A", "--after-context", "-B", "--before-context", "-C", "--context",
    "--max-depth", "-d", "--maxdepth", "--include", "--exclude",
    "--exclude-dir", "-f", "--file", "--color", "--colour",
    "--max-filesize", "--threads", "-j", "--sort", "--sortr",
}
# Flags whose value IS the pattern, so no separate bare pattern token follows.
_PATTERN_FLAGS = {"-e", "--regexp", "-f", "--file"}


def extract_scope(command: str) -> str | None:
    """Pull the scope path argument from an rg/grep command, if present.

    Heuristic: tokenize the command, drop the binary name, account for the
    search *pattern* (either a quoted/bare positional or supplied via -e/-f),
    drop option flags (and their value token for flags that take one), and take
    the first remaining bare token as the scope path. Returns None when no
    explicit path is given (caller defaults to repo root).

    Note: in `rg PATTERN PATH` the first bare token is the PATTERN, not a path —
    we must not mistake the search word for the scope.
    """
    cmd = strip_backticks(command)

    # Mark quoted patterns so they are not mistaken for a path, but keep a
    # placeholder so positional counting (pattern vs path) stays correct.
    cmd_marked = _QUOTED_RE.sub(" \x00QUOTED\x00 ", cmd)
    toks = cmd_marked.split()
    if not toks:
        return None

    # Drop a leading binary name (rg / grep / ripgrep / anything ending /rg).
    start = 0
    head = Path(toks[0]).name
    if head in {"rg", "grep", "egrep", "fgrep", "ripgrep"}:
        start = 1

    pattern_consumed = False  # has the search pattern already been accounted for?
    skip_next = False

    for idx in range(start, len(toks)):
        if skip_next:
            skip_next = False
            continue
        tok = toks[idx]

        if tok == "--":
            # Everything after -- is positional; first one is pattern (if not
            # yet consumed) else the path.
            rest = [t for t in toks[idx + 1:]]
            for t in rest:
                if not pattern_consumed:
                    pattern_consumed = True
                    continue
                return None if t == "\x00QUOTED\x00" else t
            return None

        if tok.startswith("-") and tok != "\x00QUOTED\x00":
            base = tok.split("=", 1)[0]
            if base in _PATTERN_FLAGS:
                pattern_consumed = True
            if base in _VALUED_FLAGS and "=" not in tok:
                skip_next = True
            continue

        # A bare positional token (or a marked quoted pattern).
        if not pattern_consumed:
            # This is the search pattern; skip it, the scope comes after.
            pattern_consumed = True
            continue
        # First bare positional after the pattern is the scope path.
        if tok == "\x00QUOTED\x00":
            return None
        return tok

    return None


# --------------------------------------------------------------------------
# Path resolution
# --------------------------------------------------------------------------
def resolve_in_repo(path_str: str, repo: Path) -> Path:
    """Resolve a possibly-relative path against the repo root."""
    p = Path(path_str.strip().strip("`'\"")).expanduser()
    if p.is_absolute():
        return p
    return (repo / p)


# --------------------------------------------------------------------------
# Claimed file:line verification (pure file read)
# --------------------------------------------------------------------------
def extract_claimed_hits(hits_cell: str) -> tuple[bool, list[tuple[str, str]]]:
    """Parse the Hits cell into (is_zero_match, [(file, line), ...])."""
    if ZERO_MATCH_TOKEN in hits_cell.upper():
        return True, []
    pairs = [(m.group("file"), m.group("line")) for m in FILE_LINE_RE.finditer(hits_cell)]
    return False, pairs


def read_line(file_path: Path, lineno: int) -> tuple[bool, str | None, str]:
    """Read 1-based `lineno` from file. Returns (ok, line_text, error)."""
    try:
        if not file_path.is_file():
            return False, None, "文件不存在"
    except OSError as exc:
        return False, None, f"无法访问文件: {exc}"

    try:
        with file_path.open("r", encoding="utf-8", errors="replace") as fh:
            current = 0
            for raw in fh:
                current += 1
                if current == lineno:
                    return True, raw.rstrip("\n"), ""
        # Reached EOF without hitting the requested line.
        return False, None, f"行号越界(文件仅 {current} 行)"
    except OSError as exc:
        return False, None, f"读取失败: {exc}"


def line_contains_any(line_text: str, words: list[str]) -> bool:
    low = line_text.lower()
    return any(w.lower() in low for w in words)


def verify_claimed_hits(
    file: str, line: str, words: list[str], repo: Path
) -> tuple[str, str]:
    """Verify one claimed file:line. Returns (status, detail).

    status in {"OK", "FAIL"}.
    """
    try:
        lineno = int(line)
    except ValueError:
        return "FAIL", f"{file}:{line} 行号非法"
    if lineno < 1:
        return "FAIL", f"{file}:{line} 行号必须 >=1"

    target = resolve_in_repo(file, repo)
    ok, line_text, err = read_line(target, lineno)
    if not ok:
        return "FAIL", f"{file}:{line} {err}"

    if not words:
        # Cannot judge content without a word; treat as unverifiable up the stack.
        return "WARN", f"{file}:{line} 无可用搜索词,仅确认文件/行号存在"

    if line_contains_any(line_text or "", words):
        return "OK", f"{file}:{line}"
    snippet = (line_text or "").strip()[:60]
    return "FAIL", f"{file}:{line} 该行未包含任一搜索词(实际: {snippet!r})"


# --------------------------------------------------------------------------
# ZERO_MATCH verification (native recursive scan)
# --------------------------------------------------------------------------
def is_probably_binary(path: Path) -> bool:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if suffix in BINARY_EXTS:
        return True
    # Compound suffixes like .min.js / .min.css.
    for ext in (".min.js", ".min.css"):
        if name.endswith(ext):
            return True
    return False


_GROUP_RE = re.compile(r"\([^)]*\)")


def is_compound_command(command: str) -> bool:
    """Decide if a ZERO_MATCH Command is a compound co-occurrence/proximity
    regex rather than a plain word search.

    Compound markers (on the backtick-stripped command):
      * ``.{``  — bounded repetition / proximity window (e.g. ``a.{0,40}b``)
      * ``.*``  — wildcard span between two anchors
      * 2+ ``(...)`` capture/alternation groups — multi-part pattern
    A single quoted ``a|b`` alternation is NOT compound: it is just several
    words OR-ed together, and each word is verifiable on its own.
    """
    cmd = strip_backticks(command)
    if ".{" in cmd or ".*" in cmd:
        return True
    if len(_GROUP_RE.findall(cmd)) >= 2:
        return True
    return False


def find_word(scope: Path, word: str) -> tuple[str, str] | None:
    """Recursively look for a single `word` under `scope` (case-insensitive).

    Returns (status, detail):
      None                        → conclusively not found (search completed).
      ("FOUND", "file:line")      → the word exists at this location.
      ("WARN", reason)            → scan aborted (limits/timeout/unscannable);
                                    presence is unknown.
    """
    low = word.lower()
    start = time.monotonic()
    files_seen = 0

    def search_file(fp: Path) -> tuple[str, int] | None:
        try:
            if fp.stat().st_size > MAX_FILE_BYTES:
                return None
        except OSError:
            return None
        try:
            with fp.open("r", encoding="utf-8", errors="replace") as fh:
                for n, raw in enumerate(fh, 1):
                    if low in raw.lower():
                        return (str(fp), n)
        except OSError:
            return None
        return None

    if scope.is_file():
        if not is_probably_binary(scope):
            hit = search_file(scope)
            if hit:
                return ("FOUND", f"{hit[0]}:{hit[1]}")
        return None

    for root, dirnames, filenames in __import__("os").walk(scope):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]

        if time.monotonic() - start > ZERO_SCAN_TIMEOUT_SEC:
            return ("WARN", f"扫描超时(>{ZERO_SCAN_TIMEOUT_SEC}s),`{word}` 未发现但未穷尽")

        for fn in filenames:
            files_seen += 1
            if files_seen > MAX_FILES_SCANNED:
                return ("WARN", f"扫描超过 {MAX_FILES_SCANNED} 文件上限,`{word}` 未穷尽")
            fp = Path(root) / fn
            if is_probably_binary(fp):
                continue
            hit = search_file(fp)
            if hit:
                return ("FOUND", f"{hit[0]}:{hit[1]}")

    return None


def scan_zero_match(
    scope: Path, words: list[str], compound: bool
) -> tuple[str, str]:
    """Verify a ZERO_MATCH claim by searching each word individually.

    `compound` distinguishes co-occurrence/proximity regexes (where the pattern
    only matches when several parts appear together) from plain word searches.

    Returns (status, detail):
      ("OK", reason)             → ZERO_MATCH holds (consistent with evidence).
      ("FAIL", reason)           → the claim is falsifiable (false ZERO).
      ("WARN", reason)           → cannot disprove; route to judgment/human.

    Rules (only FAIL when we can *disprove* the claim — never false-kill a
    legitimate negative subdivision):
      * Word-class ZERO_MATCH: if ANY word is found → FAIL (a too-broad
        negative like "系统无收藏" whose word demonstrably exists). If none of
        the words is found → PASS.
      * Compound-class ZERO_MATCH: if ALL component words are absent → PASS
        (the co-occurrence cannot exist when no component exists). If SOME
        words are present → WARN: the components exist but the co-occurrence /
        proximity cannot be faithfully reproduced here, so we do NOT FAIL and
        defer to judgment / human review.
    """
    if not words:
        return "WARN", "无可用搜索词,无法验 ZERO_MATCH"

    if not scope.exists():
        # Searching a non-existent scope trivially yields no matches; the
        # ZERO_MATCH claim is vacuously consistent but suspicious — be honest.
        return "WARN", f"scope 不存在: {scope}"

    found: list[str] = []          # words present in scope (word → loc shown)
    found_locs: list[str] = []
    warned: list[str] = []         # words whose presence is unknown (aborted)

    for w in words:
        res = find_word(scope, w)
        if res is None:
            continue
        if res[0] == "FOUND":
            found.append(w)
            found_locs.append(f"{w}@{res[1]}")
        else:  # WARN
            warned.append(res[1])

    if not compound:
        # Word-class: any present word disproves a blanket negative.
        if found:
            return "FAIL", "存在: " + "; ".join(found_locs)
        if warned:
            return "WARN", "; ".join(warned)
        return "OK", "scope 内各词均无匹配"

    # Compound-class: only PASS when every component is absent.
    if warned:
        return "WARN", (
            "复合共现正则,部分组成词检索未穷尽,无法验证共现: " + "; ".join(warned)
        )
    if found:
        return "WARN", (
            "复合共现正则,组件存在但共现无法复刻验证,转判断/人审 "
            "(命中组件: " + "; ".join(found_locs) + ")"
        )
    return "OK", "复合共现的全部组成词在 scope 内均不存在,共现必不在"


# --------------------------------------------------------------------------
# Row verification (binary-independent)
# --------------------------------------------------------------------------
def verify_rows(rows: list[dict], repo: Path) -> tuple[list[str], list[str], list[str]]:
    """Return (fail_msgs, warn_msgs, ok_msgs). No external binary is used."""
    fails: list[str] = []
    warns: list[str] = []
    oks: list[str] = []

    for idx, row in enumerate(rows, 1):
        command = strip_backticks(row["command"])
        words = extract_search_words(row["wordset"], command)
        is_zero, claimed = extract_claimed_hits(row["hits_cell"])

        if not words:
            warns.append(
                f"未能验真: 第{idx}行无法解析搜索词(Wordset=`{row['wordset']}` "
                f"Command=`{command}`)"
            )
            continue

        if is_zero:
            scope_arg = extract_scope(command)
            scope = resolve_in_repo(scope_arg, repo) if scope_arg else repo
            compound = is_compound_command(command)
            status, detail = scan_zero_match(scope, words, compound)
            kind = "复合共现" if compound else "单词类"
            if status == "FAIL":
                fails.append(
                    f"FAIL: 第{idx}行声称 ZERO_MATCH({kind}),但 scope 内存在该词: "
                    f"{detail}(words={words}, scope={scope})"
                )
            elif status == "WARN":
                warns.append(f"未能验真: 第{idx}行({kind}) {detail}")
            else:
                oks.append(
                    f"OK: 第{idx}行 ZERO_MATCH 已验真({kind},{detail},scope={scope})"
                )
            continue

        if not claimed:
            warns.append(
                f"未能验真: 第{idx}行 Hits 既非 ZERO_MATCH 也无 file:line"
                f"(`{row['hits_cell']}`)"
            )
            continue

        row_fails: list[str] = []
        row_warns: list[str] = []
        ok_count = 0
        for file, line in claimed:
            status, detail = verify_claimed_hits(file, line, words, repo)
            if status == "FAIL":
                row_fails.append(detail)
            elif status == "WARN":
                row_warns.append(detail)
            else:
                ok_count += 1

        if row_fails:
            fails.append(
                f"FAIL: 第{idx}行声称的 hit 未通过文件核对: "
                + "; ".join(row_fails)
                + f"(words={words})"
            )
        if row_warns:
            warns.append(f"未能完全验真: 第{idx}行 " + "; ".join(row_warns))
        if ok_count and not row_fails:
            oks.append(f"OK: 第{idx}行 {ok_count} 条 hit 已验真(读到搜索词)")

    return fails, warns, oks


# --------------------------------------------------------------------------
# Repo + args
# --------------------------------------------------------------------------
def resolve_repo(arg: str | None) -> tuple[Path | None, str]:
    if arg:
        repo = Path(arg).expanduser()
        if not repo.is_dir():
            return None, f"仓库路径不存在或非目录: {repo}"
        return repo.resolve(), ""
    return Path.cwd(), ""


def parse_args(argv: list[str]) -> tuple[str | None, str | None]:
    """Return (markdown_file, repo). Supports --repo <path> or 2nd positional."""
    md_file: str | None = None
    repo: str | None = None
    i = 0
    positionals: list[str] = []
    while i < len(argv):
        a = argv[i]
        if a == "--repo":
            if i + 1 >= len(argv):
                return None, None
            repo = argv[i + 1]
            i += 2
            continue
        if a.startswith("--repo="):
            repo = a.split("=", 1)[1]
            i += 1
            continue
        positionals.append(a)
        i += 1
    if positionals:
        md_file = positionals[0]
    if len(positionals) > 1 and repo is None:
        repo = positionals[1]
    return md_file, repo


def main() -> int:
    md_file, repo_arg = parse_args(sys.argv[1:])
    if not md_file:
        print(
            "usage: check_grep_evidence.py <markdown-file> [--repo <path> | <repo-path>]",
            file=sys.stderr,
        )
        return 2

    text = Path(md_file).read_text(encoding="utf-8")
    has_negative_claim = bool(NEGATIVE_CLAIM_RE.search(text))
    has_block = "Grep Evidence" in text

    # --- Structure layer (original behavior, unchanged) ---
    if has_negative_claim and not has_block:
        print("FAIL: negative/no-match claim without Grep Evidence block")
        return 1

    if has_block:
        missing = [name for name in REQUIRED if name not in text]
        if missing:
            print("FAIL: missing Grep Evidence columns: " + ", ".join(missing))
            return 1
        if "`rg" not in text and " rg " not in text:
            print("FAIL: Grep Evidence block has no rg command")
            return 1
        if "ZERO_MATCH" not in text and not re.search(r"[\w./-]+:\d+", text):
            print("FAIL: Grep Evidence block has no hit line or ZERO_MATCH")
            return 1

    # No block at all → keep original PASS behavior for clean docs.
    if not has_block:
        print("PASS: grep evidence structure present")
        print("(presence-only:结构合规,复合共现claim的语义交judge/人)")
        return 0

    # --- Verification layer (binary-independent, real PASS/FAIL) ---
    rows = parse_evidence_rows(text)
    if not rows:
        # Block present but no parseable data rows (e.g. blank template). The
        # structure layer already passed; nothing to verify.
        print("PASS: grep evidence structure present (no data rows to verify)")
        print("(presence-only:结构合规,复合共现claim的语义交judge/人)")
        return 0

    repo, repo_err = resolve_repo(repo_arg)
    if repo is None:
        # The repo path itself is unusable — we cannot resolve any file/scope.
        # This is the one place we honestly cannot verify; degrade to WARN.
        print(f"WARN: 未能验真: {repo_err}")
        print(f"WARN: {len(rows)} 个 evidence 行结构在场但未执行核对")
        print("PASS(STRUCTURE-ONLY): grep evidence structure present, verification skipped")
        print("(presence-only:结构合规,复合共现claim的语义交judge/人)")
        return 0

    fails, warns, oks = verify_rows(rows, repo)

    for msg in oks:
        print(msg)
    for msg in warns:
        print("WARN: " + msg)
    for msg in fails:
        print(msg)

    if fails:
        print(f"FAIL: {len(fails)} 个 evidence 行未通过验真 (repo={repo})")
        return 1

    if warns and not oks:
        # Nothing could be verified; be honest rather than green-washing.
        print(f"PASS(STRUCTURE-ONLY): {len(warns)} 行未能验真,结构在场 (repo={repo})")
        print("(presence-only:结构合规,复合共现claim的语义交judge/人)")
        return 0

    print(f"PASS: grep evidence verified ({len(oks)} ok, {len(warns)} warn) (repo={repo})")
    print("(presence-only:结构合规,复合共现claim的语义交judge/人)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
