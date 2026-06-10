#!/usr/bin/env python3
"""Scan tracked source for forbidden competitor AI references (Section 7B)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Directories / globs to scan (application + docs judges read)
SCAN_ROOTS = [
    ROOT / "app",
    ROOT / "modex_mcp",
    ROOT / "frontend" / "src",
    ROOT / "docs",
    ROOT / "scripts",
    ROOT / "tests",
]
SCAN_FILES = [
    ROOT / "README.md",
    ROOT / "JUDGES.md",
    ROOT / "SUBMISSION.md",
    ROOT / "CONFIGURATION.md",
]

SKIP_DIR_NAMES = {"node_modules", "dist", ".venv", "__pycache__", ".git"}
SKIP_FILE_NAMES = {"check_hackathon_compliance.py", "HACKATHON_COMPLIANCE.md", ".requirements.txt"}

# Case-insensitive forbidden product names (word boundary where possible)
FORBIDDEN_PATTERNS = [
    re.compile(r"\bcursor\b", re.I),
    re.compile(r"\bclaude\b", re.I),
    re.compile(r"\banthropic\b", re.I),
    re.compile(r"\bcopilot\b", re.I),
    re.compile(r"\bwindsurf\b", re.I),
    re.compile(r"\bopenai\b", re.I),
    re.compile(r"~/.cursor/", re.I),
    re.compile(r"\.cursor/mcp", re.I),
    re.compile(r"MODEX_AGENT_TOOL[\"']?\s*:\s*[\"']cursor", re.I),
]

# Allow CSS cursor property and compliance doc that lists forbidden tools
ALLOW_LINE = re.compile(
    r"cursor:\s*(pointer|default|not-allowed|grab|text)|"
    r"No OpenAI,\s*no Anthropic|"
    r"Not present in this repository|"
    r"FORBIDDEN_PATTERNS|"
    r"competitor AI|"
    r"forbidden competitor",
    re.I,
)

SKIP_FILE_NAMES = {
    "check_hackathon_compliance.py",
    "HACKATHON_COMPLIANCE.md",
    ".requirements.txt",
}


def iter_files() -> list[Path]:
    out: list[Path] = []
    for base in SCAN_ROOTS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIR_NAMES for part in path.parts):
                continue
            if path.name in SKIP_FILE_NAMES:
                continue
            if path.suffix.lower() in {".pyc", ".map", ".lock"}:
                continue
            out.append(path)
    for path in SCAN_FILES:
        if path.is_file() and path.name not in SKIP_FILE_NAMES:
            out.append(path)
    return sorted(set(out))


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    hits: list[tuple[int, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return hits
    for i, line in enumerate(text.splitlines(), 1):
        if ALLOW_LINE.search(line):
            continue
        for pat in FORBIDDEN_PATTERNS:
            if pat.search(line):
                hits.append((i, line.strip()[:120], pat.pattern))
                break
    return hits


def main() -> int:
    violations: list[tuple[Path, list[tuple[int, str, str]]]] = []
    for path in iter_files():
        hits = scan_file(path)
        if hits:
            violations.append((path, hits))

    if violations:
        print("FAIL — competitor AI references found:\n")
        for path, hits in violations:
            rel = path.relative_to(ROOT)
            print(f"  {rel}")
            for line_no, snippet, pat in hits[:5]:
                snippet = snippet.encode("ascii", "replace").decode("ascii")
                print(f"    L{line_no}: {snippet}")
            if len(hits) > 5:
                print(f"    ... +{len(hits) - 5} more")
        print("\nFix these before submission. See docs/HACKATHON_COMPLIANCE.md")
        return 1

    print("PASS — no forbidden competitor AI references in scanned paths.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
