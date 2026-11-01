#!/usr/bin/env python3
"""Build index.html for an SVG blueprint folder.

Usage: python build_doc.py <blueprint-dir>

Scans the unit folders tokens/, flow/, components/*/ and screens/*/,
flattens every SVG into _build/ (relative <image> hrefs and CSS url()
references inlined as data URIs), and writes index.html with states side
by side, status badges, spec and log text, and implementation screenshots
from shots/<unit path>/ when present. Drawings are inlined into index.html
in their own shadow roots, so the fonts in the Assets table of
inventory.md, declared once on the page, reach every drawing; an SVG shown
through <img> may load no external file at all. Declined assets are listed
at the top of the page. _build/clean/ holds the drawings without
annotation and context groups, as references for visual tests. Exits 1
when any warning was printed, since a warning can leave a reference wrong.
Standard library only.
"""

import base64
import html
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

MIME = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}
FONT_MIME = {".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".otf": "font/otf"}
FONT_FORMAT = {".woff2": "woff2", ".woff": "woff", ".ttf": "truetype", ".otf": "opentype"}
IMAGE_HREF = re.compile(r'(<image\b[^>]*?\b(?:xlink:)?href=")([^"#][^"]*)(")', re.S)
CSS_URL = re.compile(r'''(url\(\s*["']?)([^"')#][^"')]*?)(["']?\s*\))''')
EXTERNAL_USE = re.compile(r'<use\b[^>]*?\bhref="([^"#][^"]*)', re.S)
FONT_ATTR = re.compile(r'''\bfont-family=(?:"([^"]*)"|'([^']*)')''')
FONT_CSS = re.compile(r'font-family\s*:\s*([^;}"<]+)')
GENERIC_FONTS = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui", "ui-serif",
                 "ui-sans-serif", "ui-monospace", "ui-rounded", "emoji", "math", "fangsong", "inherit"}
SIZE_ATTR = re.compile(r'<svg\b[^>]*?\bwidth="([\d.]+)(?:px)?"', re.S)
STATUSES = ("draft", "review", "approved", "reconfirm", "reopened")
# a placed component shows the UI only; its notes and backdrop stay in its own entry
PLACED_STRIP = ("annotation", "context")
SHADOW_CSS = ":host{display:block}svg{display:block;width:100%;height:auto;image-rendering:pixelated}"
ET.register_namespace("", "http://www.w3.org/2000/svg")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
warnings = []


def warn(message):
    warnings.append(message)
    print(f"warning: {message}", file=sys.stderr)


def strip_classes(text, classes, source):
    """Remove every element whose class list contains one of classes."""
    if not classes:
        return text
    try:
        root = ET.fromstring(text)
    except ET.ParseError as err:
        warn(f"{source}: not stripped, XML parse error: {err}")
        return text
    drop = set(classes)
    for parent in root.iter():
        for child in list(parent):
            if drop & set(child.get("class", "").split()):
                parent.remove(child)
    return ET.tostring(root, encoding="unicode")


def data_uri(data, mime):
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def flatten(svg_path, strip=(), depth=0):
    """Return SVG text with relative <image> hrefs and url() refs inlined as data URIs.

    strip lists classes removed from this file; placed SVGs always lose
    PLACED_STRIP as well.
    """
    text = strip_classes(svg_path.read_text(encoding="utf-8"), strip, svg_path)
    if depth > 5:
        return text
    nested = tuple(set(strip) | set(PLACED_STRIP))
    if depth == 0:
        for href in EXTERNAL_USE.findall(text):
            warn(f"{svg_path}: external <use href=\"{href}\"> cannot be inlined; "
                 "place the file with <image> or copy the shape in")

    def inline(match):
        href = match.group(2).strip()
        if href.startswith("data:"):
            return match.group(0)
        if href.startswith(("http:", "https:", "//")):
            if depth == 0:
                warn(f"{svg_path}: remote resource {href}: add it to the Assets table "
                     "of inventory.md and reference the local file")
            return match.group(0)
        target = (svg_path.parent / href).resolve()
        if not target.is_file():
            warn(f"{svg_path}: missing file {href}")
            return match.group(0)
        if target.suffix.lower() == ".svg":
            data = flatten(target, nested, depth + 1).encode("utf-8")
        else:
            data = target.read_bytes()
        mime = MIME.get(target.suffix.lower()) or FONT_MIME.get(target.suffix.lower(), "application/octet-stream")
        return match.group(1) + data_uri(data, mime) + match.group(3)

    return CSS_URL.sub(inline, IMAGE_HREF.sub(inline, text))


def read_assets(root):
    """Return the rows of the Assets table in inventory.md as dicts keyed by lower-case header."""
    inventory = root / "inventory.md"
    if not inventory.is_file():
        return []
    rows, header = [], None
    for line in inventory.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            header = None
            continue
        cells = [c.strip().strip("`").strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            if cells and cells[0].lower() == "asset":
                header = [c.lower() for c in cells]
            continue
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def check_assets(root, rows):
    """Warn on unusable rows; return (@font-face CSS, font families, declined rows)."""
    faces, families, declined = [], set(), []
    for row in rows:
        name, kind = row.get("asset", ""), row.get("kind", "").lower()
        decision = row.get("decision", "").lower()
        where = f"inventory.md asset {name!r}"
        if not decision or decision.startswith("pending"):
            warn(f"{where}: no decision yet; the user decides to download or decline it (step 1)")
            continue
        if kind == "font":
            families.add(name.lower())
        if decision.startswith("declined"):
            declined.append(row)
            continue
        if row.get("source", "").lower() == "system":
            continue
        path = row.get("path", "")
        target = (root / path).resolve() if path else None
        if not target or not target.is_file():
            warn(f"{where}: file not found at {path or '(no path)'}")
            continue
        if kind == "font":
            ext = target.suffix.lower()
            if ext not in FONT_MIME:
                warn(f"{where}: unsupported font file {target.name}")
                continue
            faces.append(f'@font-face{{font-family:"{name}";'
                         f'src:url({data_uri(target.read_bytes(), FONT_MIME[ext])}) format("{FONT_FORMAT[ext]}")}}')
    return "\n".join(faces), families, declined


def check_fonts(svg_path, text, families):
    """Warn on font families a drawing names that the Assets table does not list."""
    named = [m.group(1) or m.group(2) or "" for m in FONT_ATTR.finditer(text)]
    named += FONT_CSS.findall(text)
    for stack in named:
        for family in html.unescape(stack).split(","):
            family = family.strip().strip("'\"").strip()
            if family and family.lower() not in GENERIC_FONTS and family.lower() not in families:
                warn(f"{svg_path}: font {family!r} is not in the Assets table of inventory.md (step 1)")


def inline_svg(text):
    """SVG text ready to sit inside an HTML shadow root."""
    return re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>", "", text).strip()


def drawing(text, style):
    # a shadow root per drawing keeps its <style> and ids apart, while page @font-face still applies
    return (f'<div class="drawing"{style}><template shadowrootmode="open">'
            f"<style>{SHADOW_CSS}</style>{inline_svg(text)}</template></div>")


def read_spec(spec):
    """Return (front-matter dict, body text) from a spec markdown file."""
    if not spec.is_file():
        return {}, ""
    text = spec.read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---"):
        head, sep, rest = text[3:].partition("\n---")
        if sep:
            for line in head.splitlines():
                key, colon, value = line.partition(":")
                if colon:
                    # a comment starts at " #", so values like #ff0000 survive
                    meta[key.strip()] = re.split(r"\s#", value.strip(), maxsplit=1)[0].strip()
            text = rest.lstrip("\n")
    return meta, text.strip()


def state_order(body):
    """Sort key: default first, then the order states are first named in spec.md."""
    def key(path):
        base = path.stem.split(".")[0]
        found = re.search(rf"\b{re.escape(base)}\b", body)
        return (0 if base == "default" else 1, found.start() if found else len(body), path.stem)
    return key


def svg_width(text):
    m = SIZE_ATTR.search(text)
    return float(m.group(1)) if m else None


def badge(status, where):
    if status not in STATUSES:
        warn(f"{where}: unknown status {status!r}")
    s = html.escape(status)
    return f'<span class="badge {s}">{s}</span>'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_item(root, folder, build, families):
    rel = folder.relative_to(root)
    meta, body = read_spec(folder / "spec.md")
    status = meta.get("status", "draft")
    svgs = sorted((p for p in folder.glob("*.svg") if p.stem != "transitions"),
                  key=state_order(body))
    cards = []
    for svg in svgs:
        check_fonts(svg, svg.read_text(encoding="utf-8"), families)
        flat = flatten(svg)
        out = build / rel / svg.name
        write(out, flat)
        write(build / "clean" / rel / svg.name, flatten(svg, PLACED_STRIP))
        width = svg_width(flat)
        style = f' style="--w:{width:g}px"' if width else ""
        shot = root / "shots" / rel / (svg.stem + ".png")
        shot_html = ""
        if shot.is_file():
            # captured at 1x, so it scales with the same nominal width as the drawing
            shot_html = (f'<figure class="shot"><img{style} src="{shot.relative_to(root).as_posix()}" alt="">'
                         f"<figcaption>implementation</figcaption></figure>")
        cards.append(
            f'<div class="state"><figure>{drawing(flat, style)}'
            f"<figcaption>{html.escape(svg.stem)}</figcaption></figure>{shot_html}</div>")
    transitions = folder / "transitions.svg"
    trans_html = ""
    if transitions.is_file():
        check_fonts(transitions, transitions.read_text(encoding="utf-8"), families)
        flat = flatten(transitions)
        write(build / rel / "transitions.svg", flat)
        width = svg_width(flat)
        style = f' style="width:{width:g}px"' if width else ""
        trans_html = f'<h4>transitions</h4><div class="transitions">{drawing(flat, style)}</div>'
    facts = " · ".join(f"{html.escape(k)}: {html.escape(v)}"
                       for k, v in meta.items() if k != "status")
    spec_html = f"<details><summary>spec</summary><pre>{html.escape(body)}</pre></details>" if body else ""
    log = folder / "log.md"
    if log.is_file():
        spec_html += f"<details><summary>log</summary><pre>{html.escape(log.read_text(encoding='utf-8').strip())}</pre></details>"
    anchor = html.escape(rel.as_posix().replace("/", "-"))
    return status, (
        f'<section id="{anchor}">'
        f"<h3>{html.escape(folder.name)} {badge(status, folder / 'spec.md')}</h3>"
        f'<p class="facts">{facts}</p>'
        f'<div class="states">{"".join(cards) or "<p>(no states drawn yet)</p>"}</div>'
        f"{trans_html}{spec_html}</section>")


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root{{--bg:#f6f6f4;--fg:#1d1d1b;--muted:#6b6b66;--card:#fff;--line:#deded9;
--check:#ececea;--draft:#8a8a85;--review:#b07d00;--approved:#2e7d32;--reconfirm:#6a4fb3;--reopened:#c62828;--scale:2}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#161615;--fg:#ececea;
--muted:#9a9a95;--card:#1f1f1e;--line:#33332f;--check:#2a2a28}}}}
:root[data-theme="dark"]{{--bg:#161615;--fg:#ececea;--muted:#9a9a95;--card:#1f1f1e;--line:#33332f;--check:#2a2a28}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}}
header{{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);
padding:12px 16px;display:flex;gap:16px;align-items:center;flex-wrap:wrap;z-index:1}}
header h1{{font-size:18px;margin:0}} header .muted{{color:var(--muted);font-size:13px}}
main{{padding:0 16px 48px;max-width:1400px;margin:0 auto}}
nav a{{color:inherit;margin-right:10px;font-size:13px}}
section{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px;margin:16px 0}}
h2{{margin:32px 0 0}} h3{{margin:0 0 4px}} h4{{margin:16px 0 8px;color:var(--muted)}}
.facts{{color:var(--muted);font-size:13px;margin:0 0 12px}}
.states{{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start}}
.state{{display:flex;gap:8px}}
figure{{margin:0}} figcaption{{font-size:12px;color:var(--muted);margin-top:4px}}
.states .drawing,.states img{{display:block;background:repeating-conic-gradient(var(--check) 0 25%,transparent 0 50%) 0 0/16px 16px;
image-rendering:pixelated;max-width:100%}}
.states .drawing[style],.states img[style]{{width:calc(var(--w) * var(--scale))}}
.shot img{{outline:2px dashed var(--muted)}}
.transitions .drawing{{max-width:100%}}
.assets{{border:1px solid var(--reopened);border-radius:8px;padding:8px 16px;margin:16px 0}}
.assets h2{{margin:8px 0;font-size:16px;color:var(--reopened)}}
{fonts}
.badge{{font-size:12px;font-weight:600;color:#fff;border-radius:999px;padding:1px 8px;vertical-align:middle}}
.badge.draft{{background:var(--draft)}} .badge.review{{background:var(--review)}}
.badge.approved{{background:var(--approved)}} .badge.reopened{{background:var(--reopened)}}
.badge.reconfirm{{background:var(--reconfirm)}}
pre{{white-space:pre-wrap;font-size:13px;background:var(--bg);padding:12px;border-radius:6px}}
button{{font:inherit;font-size:13px;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:2px 8px;cursor:pointer}}
button[aria-pressed="true"]{{border-color:var(--fg)}}
</style></head><body>
<header><h1>{title}</h1><span class="muted">{summary} · built {built}</span>
<span>zoom <button data-s="1">1x</button><button data-s="2" aria-pressed="true">2x</button><button data-s="4">4x</button></span>
<nav>{nav}</nav></header>
<main>{body}</main>
<script>
document.querySelectorAll('button[data-s]').forEach(b=>b.onclick=()=>{{
document.documentElement.style.setProperty('--scale',b.dataset.s);
document.querySelectorAll('button[data-s]').forEach(x=>x.setAttribute('aria-pressed',x===b));}});
</script></body></html>
"""


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        sys.exit(f"not a directory: {root}")
    build = root / "_build"
    # rebuilt from scratch so a deleted state never lingers as a stale test reference
    shutil.rmtree(build, ignore_errors=True)
    fonts, families, declined = check_assets(root, read_assets(root))
    parts, nav, counts = [], [], {}
    if declined:
        items = "".join(f"<li><b>{html.escape(r.get('asset', ''))}</b> ({html.escape(r.get('kind', ''))}): "
                        f"{html.escape(r.get('decision', ''))}</li>" for r in declined)
        parts.append('<div class="assets"><h2>Missing assets</h2><p>The user declined these; drawings '
                     f"that use them show fallbacks, so what they look like here is not final.</p><ul>{items}</ul></div>")
    groups = [("tokens", "Tokens", [root / "tokens"]), ("flow", "Flow", [root / "flow"])]
    for kind in ("components", "screens"):
        groups.append((kind, kind.capitalize(),
                       sorted(p for p in (root / kind).iterdir() if p.is_dir()) if (root / kind).is_dir() else []))
    for anchor, label, folders in groups:
        folders = [f for f in folders if f.is_dir()]
        if not folders:
            continue
        parts.append(f'<h2 id="{anchor}">{label}</h2>')
        nav.append(f'<a href="#{anchor}">{anchor}</a>')
        for folder in folders:
            status, section = build_item(root, folder, build, families)
            counts[status] = counts.get(status, 0) + 1
            parts.append(section)
    summary = ", ".join(f"{n} {s}" for s, n in sorted(counts.items())) or "empty"
    title = html.escape(root.parent.parent.name if root.name == "blueprint" else root.name)
    page = PAGE.format(title=f"{title} blueprint", summary=summary, fonts=fonts,
                       built=datetime.now().strftime("%Y-%m-%d %H:%M"),
                       nav="".join(nav), body="".join(parts))
    (root / "index.html").write_text(page, encoding="utf-8")
    print(f"wrote {root / 'index.html'} ({summary})")
    if warnings:
        sys.exit(f"{len(warnings)} warning(s): fix them before trusting _build/clean/")


if __name__ == "__main__":
    main()
