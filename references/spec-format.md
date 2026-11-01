# spec.md, log.md and inventory.md format

Reference for [`SKILL.md`](../SKILL.md). Every unit folder (`tokens/`, `flow/`, `components/<name>/`, `screens/<name>/`) has two text files beside its drawings:

- `spec.md` is the **contract**: the facts the user approves together with the drawings. It is locked with them at approval (step 4) and re-locked when step 6 adds the Interface and Guardrails, so any other edit shows up in `guardrails.py check`.
- `log.md` is the **history**: changes, the red run, differences. It keeps growing and is never locked.

Sections appear in the order below; leave out a section that has no content yet. Which sections each unit uses:

| section | tokens | flow | component | screen |
|---|---|---|---|---|
| Purpose | yes | yes | yes | yes |
| States, Variants | - | - | yes | yes |
| Transitions | - | between screens | yes | yes |
| Interface, Guardrails | yes | yes | yes | yes |

## spec.md

### Front matter

```text
---
status: draft            # draft | review | approved | reconfirm | reopened
approved: 2026-11-01     # date of the user's approval; cleared on reopen
verified: 2026-11-05     # date step 8 finished; cleared on reopen
size: 120x36             # width x height; a range is 120-240x36
unit: px                 # px | pt | dp | game px; see platforms.md
---
```

One `key: value` per line; a comment starts at ` #`. For a screen, `size` is the reference resolution; tokens and flow have no `size`. `reconfirm` marks an approved unit whose appearance changed only through something it uses (a placed component, a token value) and that waits for the user to look again.

### Purpose

One or two sentences: what the unit is for, the target platform and input types.

### States

| state | looks like | notes |
|---|---|---|
| default | accent body, label | |
| disabled | muted body and label | no hover, no focus, no click |

One row per state, named exactly as its drawing without suffixes (`disabled` ↔ `disabled.svg`). Below the table, list states that do not apply and why (`Not applicable: loading, no async action`).

### Transitions

| from | to | trigger | timing |
|---|---|---|---|
| default | hover | pointer enter | 120ms ease-out |
| hover | default | pointer leave | 120ms ease-out |

One row per arrow in the unit's `transitions.svg` (for the flow, `flow.svg`); the two match one to one, worded identically. Timing is `<duration> <easing>`, or `-` for instant. In the flow, `from` and `to` are screen states written `<screen>/<state>` (`main-menu/default` → `settings/default`, trigger `select Settings`).

### Variants

Every drawing beyond the plain `<state>.svg`, with the reason it exists:

| file | why |
|---|---|
| overflow.zh-TW.svg | Chinese label is the longest |
| default.375.svg | screen: buttons stack vertically below 400 px |

Size variants on screens list only resolutions where the layout changes; a component used at another size in a screen needs a size variant (or `stretched`) drawn here.

### Interface

How tests drive the unit, written in the target platform's terms, as small as the guardrails need:

- **Inputs**: the props, parameters or model values that select a state (`disabled: bool`).
- **Triggers**: how a test fires each trigger in the Transitions table (`pointer enter` → hover event on part `body`).
- **Hooks**: how a test finds each SVG part id (`data-testid`, accessibility identifier, node name).

For tokens, the Interface names the theme artefact (CSS custom properties, a Godot `Theme` resource, a Unity USS file) and how a test reads a token's value. The stub in step 6 implements exactly the Interface, and nothing else.

### Guardrails

| guardrail | covers | file |
|---|---|---|
| button / disabled shows muted body and ignores click | state disabled | tests/guardrails/button.test.ts |
| button / pointer enter switches body to accent-hover | transition default → hover | tests/guardrails/button.test.ts |
| button / visual matches disabled.svg, tolerance 1% pixels | drawing disabled.svg | tests/guardrails/button.visual.test.ts |

`covers` names a state, a transition, a drawing or (for tokens) a token. Every state, every transition and every capturable drawing appears at least once; a screen's guardrails cover its layout and composition, not the placed components' own states. `file` is exactly one test file per row, relative to the project root; `guardrails.py check` requires every listed file of an approved unit to be locked. A value in parentheses, such as `(example)`, is not a path and is skipped. Visual guardrails state their tolerance; the user approves it with the table.

## log.md

### Changes

Dated entries, newest first: what changed, why, who approved (`2026-11-03 reopened: hover colour too close to default; approved 2026-11-04`). Written on every reopen and re-confirm.

### Red run

The guardrail run against the stub in step 6: command, counts, date.

### Differences

Written in step 8, one row per difference between a screenshot and its drawing:

| file | what differs | outcome |
|---|---|---|
| hover.svg | label 1px lower | implementation fixed |

Outcome is one of: **blueprint updated** (the user prefers the implementation; the unit is reopened and re-approved), **implementation fixed** (re-captured afterwards; a new guardrail first when the existing ones could not catch it), or **accepted** (the user said so). The agent proposes an outcome; the user decides. A drawing the platform cannot capture (often an animation key frame) gets a row with the alternative evidence the user accepted (a short recording, a frame-by-frame capture, or a note).

## inventory.md

At the blueprint root, written in step 1 and updated whenever a screen or component is added:

```text
# Inventory

Confirmed by the user: 2026-11-01

| screen | components |
|---|---|
| main-menu | button, title-logo |
| settings | button, slider, toggle |

| asset | kind | path | used by | source | licence | decision |
|---|---|---|---|---|---|---|
| Cubic 11 | font | ../../public/fonts/Cubic_11.woff2 | tokens, all text | project | OFL | available |
| Press Start 2P | font | assets/fonts/PressStart2P.ttf | title-logo | download from the designer's release page | OFL | downloaded 2026-11-01 |
| hero sprite | sprite | | main-menu backdrop | not found | unknown | declined: grey 32x32 box; backdrop shows layout only |
```

Components are listed in the order they are implemented within each slice.

Assets table: one row per font, sprite sheet, image or icon set the drawings use. `asset` for a font is the family name exactly as drawings write it in `font-family`; `path` is from the blueprint folder, pointing at the project's own file where it has one, else at `assets/`. `source` is `project`, `system` (installed on this machine only: other machines and CI render differently), or where it was downloaded from. `decision` is `available`, `downloaded <date>`, or `declined: <fallback>; <what the blueprint cannot show>`. `build_doc.py` declares every available font on the page, lists declined assets at the top of `index.html`, and warns on a row without a decision, a missing file, or a font a drawing names that is not in the table.
