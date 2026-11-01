---
name: svg-blueprint
description: Design any user interface (game UI and HUD, mobile or desktop app, web) as SVG blueprints approved component by component, turn the approved design into locked guardrail tests, then implement and verify against them. Use when a UI, screen, HUD, menu, widget or visual component is about to be designed or redesigned, when the user asks to "用 SVG 設計 / 先畫 SVG / 畫元件 / 做 mockup", or when implementing UI that already has a blueprint folder.
---

# SVG blueprint

A **blueprint** is the approved drawing the code is built from: a folder of SVG files, one per state of each component and screen. The user and the agent work from the same files: you edit the SVG text, the user looks at the rendered picture. Its job is to shrink the gap between what the user means and what you build. Code follows the blueprint; the blueprint changes only through a reopen the user approves.

This skill works for any UI and is most useful where no standard component library exists: game HUDs and menus, custom app controls, pixel-art interfaces, native toolkits with little training data. Why it is built this way, and its limits: [`docs/design-rationale.md`](docs/design-rationale.md).

Work bottom-up. Components first, each approved on its own; screens next, composed only from approved components; implementation only after that. A whole-screen mockup drawn first mixes palette, spacing, component shape, states and layout into one picture the user can only reject as a whole.

## Terms

- **Unit**: a folder approved on its own: `tokens/`, `flow/` (navigation between screens), a component or a screen. Every unit has `spec.md`, `log.md` and its SVG files.
- **Drawing**: a state or variant SVG of a unit (`hover.svg`, `overflow.zh-TW.svg`). `transitions.svg` and `flow.svg` show behaviour and are not drawings.
- **Slice**: a screen together with the components it places. Nothing in a slice is implemented until all of its units are approved.
- **Guardrail**: a test derived from an approved unit and written before the unit is implemented (step 6).
- **Lock**: hashes of approved files and guardrails in `guardrails.lock`. An SVG's hash includes every file it places, so a changed component also shows up as a change to every screen that places it.

In commands, `<skill>` is the folder containing this file and `design/blueprint` is the blueprint folder. Run every command from the project root; file arguments are paths from there.

## Folder

The blueprint lives in the project at `design/blueprint/`. If the project already keeps design files in a folder (such as `docs/design/`), put `blueprint/` inside it and use that path for `design/blueprint`; when unsure, ask. A repository with several separate UIs has one blueprint folder per UI.

```text
design/blueprint/
  inventory.md                          screens, the components each places, assets (step 1)
  assets/                               fonts and art downloaded for the blueprint (step 1)
  tokens/        spec.md log.md tokens.svg
  flow/          spec.md log.md flow.svg
  components/<component>/
                 spec.md                contract: states, transitions, variants, interface, guardrails
                 log.md                 history: changes, red run, differences
                 <state>[.<suffix>...].svg
                 transitions.svg
  screens/<screen>/                     same files as a component
  guardrails.lock
  shots/<unit path>/<drawing stem>.png  screenshots (step 8)
  _build/clean/                         generated visual references
  index.html                            generated design doc
```

File formats: [`references/spec-format.md`](references/spec-format.md) (`spec.md`, `log.md`, `inventory.md`); [`references/svg-conventions.md`](references/svg-conventions.md) (drawing, naming, suffixes); [`references/platforms.md`](references/platforms.md) (per-platform units, states, capture, test tools); [`references/project-setup.md`](references/project-setup.md) (what to commit, `.gitignore`, test harness, CI).

After any edit under the blueprint folder, run `python <skill>/scripts/build_doc.py design/blueprint`. It writes `index.html`, showing every unit with its drawings side by side (with the Assets table's fonts applied), status badges, screenshots and any declined asset at the top, and `_build/clean/`, every drawing with annotation and context groups removed: the reference visual guardrails compare against. It exits non-zero on any warning; fix warnings before trusting `_build/clean/`. To look at `index.html` yourself, serve the blueprint folder on localhost (`python -m http.server --bind 127.0.0.1`) and open it in your browser tool, or take a headless browser screenshot of the file; some agent browser panes show a local file blank.

## Steps

Order:

1. Steps 1 and 2 once for the whole UI.
2. Per slice: steps 3 and 4 for each component not yet approved, then step 5 for the screen.
3. When every unit of a slice is approved, run steps 6 to 8 per unit: `tokens/` before the first slice's components, then the slice's components in `inventory.md` order (skip any already implemented in an earlier slice), then the screen.
4. `flow/` is drawn and approved in step 5 once there are two screens, and goes through steps 6 to 8 after the screens it links are implemented; a slice that adds a screen reopens it.

A reopen (step 4) sends a unit back to step 3 or 5.

### 1. Inventory

Read the section of `platforms.md` for each platform the UI ships on. Write `inventory.md`: the screens, and for each screen the components it places. For each component, write `spec.md` with its States table: the platform's states (pointer, touch, gamepad focus), plus loading, empty, error, overflow (longest real text, in every language the UI ships) and `stretched` when its size is a range. List the states that do not apply, with the reason, below the table.

Then find the **assets** the drawings will need besides shapes and text: fonts, sprite sheets and other raster art, icons, backdrops. A drawing can show only what the blueprint folder holds: an SVG shown as an image loads no outside file, and the visual tests' rasterizer sees only what it is given. Look in the project first (asset folders, theme files, the font the code loads) and list each asset in the Assets table of `inventory.md`. For each one not found locally, the user decides:

- **Download**: name the source, licence and size; download only after the user says yes, into `design/blueprint/assets/`.
- **Decline**: say plainly what the blueprint cannot show without it, before drawing (a missing font: drawings use the fallback, so text width, truncation and every visual guardrail on text are estimates; missing art: a placeholder box of the same size), and write that consequence into the table.

Done when: `inventory.md` lists every screen with its components, every component has a `spec.md` with a States table, every asset has a decision in the Assets table, and the user has confirmed the inventory (record the date in `inventory.md`).

### 2. Tokens

Draw `tokens/tokens.svg` (colours with names and values, the type scale with the real font, spacing steps) and write `tokens/spec.md` with `status: draft`. Use only colours named in `tokens.svg`; propose any new colour to the user as a token change. Use only fonts in the Assets table; a font found later goes back to step 1 for the user's decision.

Done when: the tokens are approved and locked (step 4), together with the asset files the Assets table names.

### 3. Component states

Draw one SVG per row of the component's States table, plus one per entry in its Variants section. Draw behaviour as states, not animation: join every pair of states that a trigger connects with an arrow in `transitions.svg`, labelled `<trigger> · <duration> <easing>`, or just the trigger when the change is instant. Write the same arrows in the Transitions table of `spec.md`, one row per arrow, worded identically.

Done when: every state and variant has a drawing, every component with more than one state has a `transitions.svg` whose arrows match its Transitions table one to one, and `index.html` shows them all.

### 4. Approval

Present one unit, or the components of one screen, at a time: set `status: review` and give the user the path to `design/blueprint/index.html` (share the whole blueprint folder when sending it elsewhere). When a choice is open, offer alternatives side by side ([naming](references/svg-conventions.md#naming)).

Approval covers the drawings, `transitions.svg` (or `flow.svg`) and `spec.md` together. On the user's explicit approval of that unit, set `status: approved` and `approved:`, then lock it:

```bash
python <skill>/scripts/guardrails.py lock design/blueprint <unit path>/spec.md <unit path>/*.svg
```

**Reopen** when the unit's own design changes (states, layout, parts, a token's name or role):

1. Set `status: reopened`, clear `approved:` and `verified:`, and add a Changes entry to `log.md`.
2. Take the unit back through step 3 or 5, this step, and step 6 for its guardrails.

**Re-confirm** when a unit changed only through something it uses: a screen placing a reopened component, or units whose files a token value find-and-replace touched. `guardrails.py check` reports them as changed.

1. Set `status: reconfirm` and add a Changes entry to `log.md`.
2. Run `build_doc.py` and show the user the affected drawings.
3. On approval, set `status: approved`, re-lock the unit's `spec.md` and `*.svg`, and re-run its visual guardrails.

Unlock and re-lock only with the user's approval; the diff of `guardrails.lock` and of `_build/clean/` is what the user reviews.

Done when: the presented unit is `approved` and `guardrails.py check design/blueprint` reports nothing for it.

### 5. Screens

Write the screen's `spec.md` with its States table and draw each state from approved components only, placed with `<image>` at the referenced drawing's own size ([screens rules](references/svg-conventions.md#screens)). A screen decides layout, alignment and spacing between components; it does not redraw a component. Add anything a screen needs that no approved component provides to `inventory.md` as a new component and take it through step 3.

Draw each state at the reference resolution (no size suffix), plus each resolution, aspect ratio or breakpoint where the layout changes, listed in Variants. Place HUDs and overlays over a backdrop image (a screenshot or representative scene) inside a `context` group. Give a screen with more than one state a `transitions.svg`; once there are two screens, draw `flow/flow.svg` and write `flow/spec.md`.

Done when: every state and variant has a drawing, transitions and flow are drawn where needed, and the screen (and flow) are approved and locked (step 4).

### 6. Guardrails

Guardrails keep the implementation on the design: an agent writing tests beside its own code tends to write tests its code passes. Guardrails come from the approved design before the code exists and cover its goals (states, transitions, look); your own tests in step 7 cover implementation details. Set up the test harness once before the first unit ([project setup](references/project-setup.md#test-harness)).

Per unit, before its implementation starts:

a. Draft the Guardrails table: per state, the unit shows the part ids drawn in that state's SVG with the text and values drawn there; per transition, the trigger moves one state to the other; per drawing the platform can capture (animation key frames often cannot), a visual check against its `_build/clean/` copy ([rendering](references/platforms.md#rendering-the-blueprint-for-visual-tests)) with a tolerance. For tokens: the theme defines every token with its value. For a screen: layout and composition only; the placed components have their own guardrails. Name each `<unit> / <what it checks>`.
b. Draft the Interface: the inputs that select a state, how each trigger is fired, how each SVG part id is found (test ids, accessibility identifiers, node names); for tokens, the theme artefact and how a value is read.
c. Show the drafted table and Interface to the user next to the drawings they cover. On approval, write both into `spec.md`.
d. Write the guardrails from the blueprint alone, in the guardrail test folder, one test file per Guardrails row's `file`. When you can start a subagent, give a fresh-context subagent the unit's `spec.md`, its drawings and `_build/clean/` copies, the guardrail folder and the test command, and nothing of this unit's implementation; otherwise write the guardrails before reading or writing any implementation of the unit.
e. Implement the Interface as a stub with no behaviour, run `build_doc.py`, then run the guardrails. Each must fail on its assertion: a guardrail that passes against the stub guards nothing (`disabled ignores click` alone passes; `disabled shows the muted body and ignores click` fails until built). One that cannot run (compile error, missing setup) is broken; fix the setup. Record the run in `log.md`.
f. Lock the guardrails and re-lock `spec.md`: `python <skill>/scripts/guardrails.py lock design/blueprint <unit path>/spec.md <guardrail files>`.

Done when: the Guardrails table covers every state, transition and capturable drawing of the unit; the user approved the table and the Interface; every guardrail fails on its assertion against the stub; and `guardrails.py check design/blueprint` passes.

### 7. Implement

If a skill named `tdd` is available, load it ([source](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd)); otherwise use its cycle: one failing test, the least code to pass it, refactor only when green. Guardrails are fixed outer tests approved in step 6, each the failing test for one or more cycles, starting with the default state's structure and ending with the visual checks. Write your own tests one at a time as `tdd` directs; its planning step and its rule against writing tests in bulk apply to those tests only.

Do not edit locked files. When a guardrail looks wrong, stop and raise it with the user: it is a design question, answered by a reopen (step 4) and new guardrails (step 6). With the user's approval, run `guardrails.py unlock` to remove entries for files a reopen deleted.

Build layout with the target platform's own idioms (flex and grid, native layout containers, engine anchors and containers), never by copying SVG coordinates into absolute positions; the blueprint fixes the visual result, not the structure. Name nodes, props or classes after the SVG part ids.

Done when: every guardrail of the unit passes, your own tests pass, and `guardrails.py check design/blueprint` passes.

### 8. Verify

For each capturable drawing of the unit, capture the implementation at 1x ([capturing](references/platforms.md#capturing-at-1x)) into `shots/<unit path>/<drawing stem>.png` and run `build_doc.py`. Open `index.html` at 4x and compare each screenshot with its drawing for position, size, colour, text and truncation, together with the visual guardrails' difference images. Write every visible difference to the Differences section of `log.md` with a proposed outcome (spec-format lists them); the user decides each. For "blueprint updated", reopen the unit. For "implementation fixed", when no existing guardrail covers the difference, propose a new one; once the user agrees, write it, confirm it fails, lock it, then fix and re-capture. For a drawing the platform cannot capture, record the alternative evidence the user accepted.

Done when: every capturable drawing has a current screenshot next to it in `index.html`, every difference has an outcome the user decided, `guardrails.py check design/blueprint` passes, `verified:` is set, and you have given the user the path to `index.html`.

## Lessons

When a step's rule produced a wrong result or had to be bypassed in a real project, add a dated entry to [`LESSONS.md`](LESSONS.md) (what happened, which step, the suggested rule change); when the skill folder cannot be written, give the entry to the user instead. Rule changes land in this file only after the user agrees.
