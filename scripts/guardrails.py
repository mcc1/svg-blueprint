#!/usr/bin/env python3
"""Lock approved blueprint files and guardrail tests, and check them.

Usage (run from the project root; file paths are relative to it):
  python guardrails.py lock   <blueprint-dir> <file>...
  python guardrails.py unlock <blueprint-dir> <file>...
  python guardrails.py check  <blueprint-dir>

lock records a hash of each file in <blueprint-dir>/guardrails.lock, adding
to or replacing earlier entries. An SVG is hashed together with every local
file it references through <image href> or url(), recursively, so a screen's hash
changes when a component it places changes. unlock drops entries, for files
a reopen deleted. Re-locking and unlocking are design decisions that need
the user's approval.

check exits 1 and lists every locked file that changed or disappeared, and
every file an approved unit requires that is not locked: for each unit
folder (tokens/, flow/, components/*, screens/*) whose spec.md front matter
says status: approved, its spec.md, its .svg files and the guardrail files
named in its Guardrails table. Paths are stored relative to the blueprint
folder, so the lock survives moving the checkout. Standard library only.
"""

import hashlib
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

LOCK = "guardrails.lock"
IMAGE_HREF = re.compile(r'<image\b[^>]*?\b(?:xlink:)?href="([^"#][^"]*)"', re.S)
CSS_URL = re.compile(r'''url\(\s*["']?([^"')#][^"')]*?)["']?\s*\)''')


def digest(path, seen=None):
    # normalise line endings so a checkout with different autocrlf does not trip the check
    data = path.read_bytes().replace(b"\r\n", b"\n")
    h = hashlib.sha256(data)
    if path.suffix.lower() == ".svg":
        seen = (seen or set()) | {path}
        refs = []
        text = data.decode("utf-8", "replace")
        for href in IMAGE_HREF.findall(text) + CSS_URL.findall(text):
            href = href.strip()
            if href.startswith(("data:", "http:", "https:", "//")):
                continue
            target = (path.parent / href).resolve()
            if target in seen:
                continue
            refs.append(f"{href}:{digest(target, seen) if target.is_file() else 'missing'}")
        for ref in sorted(refs):
            h.update(b"\n" + ref.encode("utf-8"))
    return h.hexdigest()


def load(root):
    lock = root / LOCK
    if not lock.is_file():
        return {"files": {}}
    return json.loads(lock.read_text(encoding="utf-8"))


def relative(root, name):
    return Path(os.path.relpath(Path(name).resolve(), root)).as_posix()


def save(root, state):
    state["files"] = dict(sorted(state["files"].items()))
    (root / LOCK).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def lock(root, files):
    state = load(root)
    for name in files:
        path = Path(name).resolve()
        if not path.is_file():
            sys.exit(f"not a file: {name} (paths are relative to the current directory)")
        rel = relative(root, name)
        state["files"][rel] = {"sha256": digest(path), "locked": date.today().isoformat()}
        print(f"locked {rel}")
    save(root, state)


def unlock(root, files):
    # works on deleted files too, which is the usual case after a reopen
    state = load(root)
    for name in files:
        rel = relative(root, name)
        if state["files"].pop(rel, None) is None:
            sys.exit(f"not locked: {rel}")
        print(f"unlocked {rel}")
    save(root, state)


def check(root):
    entries = load(root)["files"]
    problems = []
    for rel, entry in entries.items():
        path = root / rel
        if not path.is_file():
            problems.append(f"missing     {rel}")
        elif digest(path) != entry["sha256"]:
            problems.append(f"changed     {rel} (locked {entry['locked']})")
    required = required_files(root)
    for rel in sorted(required - set(entries)):
        problems.append(f"not locked  {rel}")
    for line in problems:
        print(line)
    print(f"{len(entries)} locked, {len(required)} required by approved units, {len(problems)} problems")
    sys.exit(1 if problems else 0)


def status(spec):
    """status from the front matter only, matching build_doc.py."""
    if not spec.is_file():
        return None
    text = spec.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    head = text[3:].partition("\n---")[0]
    m = re.search(r"^status:\s*(\S+)", head, re.M)
    return m.group(1) if m else None


def guardrail_files(spec):
    """Third column of the Guardrails table, one path per row; values in parentheses are placeholders."""
    text = spec.read_text(encoding="utf-8")
    section = re.search(r"^#+\s*Guardrails\s*$(.*?)(?=^#+\s|\Z)", text, re.M | re.S)
    files = set()
    for line in (section.group(1).splitlines() if section else []):
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or set(cells[2]) <= set("-: ") or cells[2] in ("file", "") or cells[2].startswith("("):
            continue
        files.add(cells[2])
    return files


def unit_folders(root):
    singles = [root / name for name in ("tokens", "flow") if (root / name).is_dir()]
    many = [p for kind in ("components", "screens") if (root / kind).is_dir()
            for p in sorted((root / kind).iterdir()) if p.is_dir()]
    return singles + many


def required_files(root):
    """Every file approved units say must be locked, relative to the blueprint folder."""
    need = set()
    for unit in unit_folders(root):
        spec = unit / "spec.md"
        if status(spec) != "approved":
            continue
        need.add(relative(root, spec))
        need.update(relative(root, svg) for svg in unit.glob("*.svg"))
        # _build/clean/ is derived from these drawings, so it is committed but not locked
        need.update(relative(root, f) for f in guardrail_files(spec))
    return need


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("lock", "unlock", "check"):
        sys.exit(__doc__)
    command, root = sys.argv[1], Path(sys.argv[2]).resolve()
    if not root.is_dir():
        sys.exit(f"not a directory: {root}")
    if command == "check":
        check(root)
    elif len(sys.argv) < 4:
        sys.exit(f"{command} needs at least one file")
    else:
        (lock if command == "lock" else unlock)(root, sys.argv[3:])


if __name__ == "__main__":
    main()
