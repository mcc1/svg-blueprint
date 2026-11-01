# SVG conventions

Reference for steps 3 and 5 of [`SKILL.md`](../SKILL.md). Every rule here exists so that the same file renders the same way in a browser, in the generated doc, and in a diff.

## Canvas

- `viewBox` equals the unit's nominal size at 1x in the unit of measure named in `spec.md` (`viewBox="0 0 160 40"`), with matching `width` / `height`. No transform on the root group. When `size` is a range, each state is drawn at the minimum, and a `stretched` state shows the maximum.
- One state per file. The file shows the unit only, on a transparent background; context the state needs (a parent panel, the cursor for hover, a game scene behind a HUD) is drawn in a group with `class="context"` and reduced opacity so it reads as not-part-of-the-unit. A backdrop image goes inside that group as an `<image>`, so `build_doc.py` strips it from the `_build/clean/` reference.
- Keep coordinates on whole or half pixels. Pixel-art UIs use whole pixels only and `shape-rendering="crispEdges"`.

## Naming

- Root element carries `data-component="<component>"` and `data-state="<state>"`, matching the folder and file name.
- Each meaningful part is a `<g id="<part>">` with a name the implementation and the tests will reuse (`label`, `icon`, `badge`, `track`, `thumb`). These ids are the shared vocabulary between blueprint and code; pick them as you would pick component prop or class names.
- File names are `<state>[.<size>][.<lang>][.<frame>][.<alt>].svg`, each suffix optional, always in this order. A file with size, language or frame suffixes is a **variant**, listed in the Variants section of `spec.md` ([spec-format.md](spec-format.md)); an `alt` suffix only exists while a choice is open.
  - `size`: a resolution or breakpoint other than the reference one (`.375`, `.1280x720`); the reference resolution has no size part.
  - `lang`: a language tag when text differs by language (`.en`, `.zh-TW`), typically for `overflow`.
  - `frame`: an animation key frame (`.f1`, `.f2`).
  - `alt`: an alternative under review (`.a`, `.b`); when one is chosen, the others are deleted and the winner loses its `alt` part, with screen `<image>` hrefs updated to match.

  Example: `overflow.375.zh-TW.svg`. Screenshots and `_build/clean/` copies use the same file stem. Delete unchosen alternatives before locking: `guardrails.py check` requires every `.svg` in an approved unit folder to be locked.

## Colour and type

- Colours come from `tokens/tokens.svg`. Write them through a `<style>` block with classes named after tokens (`.fill-surface`, `.stroke-accent`), so a token value change is a find-and-replace of the value across files (a re-confirm for the units it touches, SKILL.md step 4) and a review can spot an off-token colour as a class that does not exist.
- Give every shape and text an explicit fill, including the default black. The doc can render on a dark background, where unset fills disappear.
- Text stays `<text>`, never converted to paths, so it remains diffable and translatable. Set `font-family` to the real product font with a generic fallback; when the product font is a pixel or web font the browser may not have, note the font and its metrics in `spec.md`, since layout depends on them.
- Draw text with the longest realistic content in the `overflow` state, and decide truncation (ellipsis, wrap, shrink) there rather than leaving it to the implementer.

## Annotations

- Measurements, notes and arrows go in a `<g class="annotation">`, coloured magenta (`#e0218a`) so they are never mistaken for UI. The doc shows them; implementation ignores them. Keep annotation and context groups flat (no nested `<g>`): `build_doc.py` strips annotations when a component is placed inside a screen, so a screen shows only UI, and strips both from the copies in `_build/clean/` that visual tests compare against.
- `transitions.svg` lays out small copies of the state frames joined by arrows. Each arrow is labelled `<trigger> · <duration> <easing>` (`pointer enter · 120ms ease-out`), or just the trigger when the change is instant, worded exactly as in the Transitions table.

## Screens

- Place components with `<image href="../../components/<component>/<state>.svg" x=".." y=".." width=".." height=".."/>`, using a relative path. Do not redraw a component inside a screen, and do not use external `<use href="file.svg#id">`: browsers block it for local files.
- `width` and `height` of each `<image>` equal the `viewBox` size of the file it references. SVG scales a placed image proportionally, so any other size distorts the component; a component shown at another size references a drawn size variant or its `stretched` state instead.
- Screens with more than one state have a `transitions.svg` like components. Navigation between screens is drawn in `flow/flow.svg`: small copies of the screens (placed with `<image href="../screens/<screen>/<state>.svg">` at reduced size, the one place scaling is allowed) joined by labelled arrows.
- Browsers also do not load external images inside an SVG shown through `<img>`, so `build_doc.py` writes a flattened copy of every screen into `_build/` with those images inlined. Open screens through `index.html`, not by opening the raw file.
