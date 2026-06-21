#!/usr/bin/env python3
"""
Verification loop for the Constellation proposal site.

This is the "verification" half of loop engineering: an agent (or CI, or a
human) can run this after every change and trust the result, instead of
eyeballing the page. It has no third-party dependencies — Python 3 stdlib
only — so it runs anywhere, including a fresh web session.

Checks performed against every *.html file in the repo:
  1. Every local href/src (assets, files) actually exists on disk.
  2. Every internal #anchor resolves to an element with that id.
  3. Tags are reasonably balanced (catches an unclosed <section> etc.).
  4. mailto: links are present and well-formed (the proposal's CTA).
  5. Repo hygiene: .nojekyll exists so GitHub Pages serves files as-is.

Exit code 0 = all green (the loop's stopping condition).
Exit code 1 = at least one failure (the loop should keep working / escalate).
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
# Void elements never need a closing tag.
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def note(msg: str) -> None:
    notes.append(msg)


class Collector(HTMLParser):
    """Collects ids, local references, mailto links, and a tag stack trace."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.local_refs: list[str] = []      # href/src pointing at local files
        self.anchors: list[str] = []         # href="#..."
        self.mailtos: list[str] = []
        self.stack: list[str] = []
        self.imbalance = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d and d["id"]:
            self.ids.add(d["id"])
        for key in ("href", "src"):
            val = d.get(key)
            if not val:
                continue
            if val.startswith("#"):
                self.anchors.append(val[1:])
            elif val.startswith("mailto:"):
                self.mailtos.append(val)
            else:
                parsed = urlparse(val)
                if not parsed.scheme and not val.startswith("//"):
                    # purely local path reference
                    self.local_refs.append(parsed.path)
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        # self-closing in source (e.g. <path/>) — treat as balanced
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag in self.stack:
            # pop back to the matching open tag
            while self.stack and self.stack.pop() != tag:
                pass
        else:
            self.imbalance = True


def check_html(path: Path) -> None:
    rel = path.relative_to(ROOT)
    parser = Collector()
    parser.feed(path.read_text(encoding="utf-8"))

    # 1. local references resolve
    for ref in parser.local_refs:
        target = (path.parent / unquote(ref)).resolve()
        if not target.exists():
            fail(f"{rel}: references missing file '{ref}'")

    # 2. internal anchors resolve
    for anchor in parser.anchors:
        if anchor and anchor not in parser.ids:
            fail(f"{rel}: anchor '#{anchor}' has no matching id")

    # 3. tag balance
    if parser.imbalance or parser.stack:
        leftover = ", ".join(parser.stack[-5:]) or "stray close tag"
        fail(f"{rel}: unbalanced tags (unclosed: {leftover})")

    # 4. mailto present and well-formed (root proposal only)
    if rel == Path("index.html"):
        if not parser.mailtos:
            fail(f"{rel}: no mailto: CTA found")
        for m in parser.mailtos:
            addr = m[len("mailto:"):].split("?", 1)[0]
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", addr):
                fail(f"{rel}: malformed mailto address '{addr}'")

    note(f"{rel}: {len(parser.ids)} ids, {len(parser.local_refs)} local refs, "
         f"{len(parser.anchors)} anchors checked")


def check_repo() -> None:
    if not (ROOT / ".nojekyll").exists():
        fail(".nojekyll missing — GitHub Pages may mangle files")


def main() -> int:
    html_files = sorted(ROOT.rglob("*.html"))
    html_files = [p for p in html_files if ".git" not in p.parts]
    if not html_files:
        fail("no .html files found")
    for path in html_files:
        check_html(path)
    check_repo()

    for n in notes:
        print(f"  · {n}")
    print()
    if failures:
        print(f"✗ {len(failures)} issue(s):")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print(f"✓ all checks passed across {len(html_files)} HTML file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
