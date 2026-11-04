# svg-blueprint: agent guide

This repository is an agent skill. The repository root is the skill folder: `SKILL.md` is what an agent loads when the skill fires; everything else is reached from it by pointer. This file is for agents changing the skill itself, not for agents using it in another project.

## What the skill is for

Every change is judged against two goals:

1. **Fewer misunderstandings** between the user and the agent: the user approves pictures, not prose, one small piece at a time.
2. **Implementation that follows the design**: approved drawings become guardrail tests, written before a unit is implemented and locked while it is implemented, and screenshots are compared back to the drawings after.

It is platform-general. Games and native apps without a standard component library are the main audience; web is one target among several. A rule that only makes sense for one platform goes in that section of `references/platforms.md`, never in `SKILL.md`.

## Layout

| Path | Role |
|---|---|
| `SKILL.md` | The steps. Always loaded when the skill fires, so it stays short: steps, each with a done-when criterion |
| `references/spec-format.md` | `spec.md` (the locked contract), `log.md` (history) and `inventory.md` |
| `references/project-setup.md` | One-time setup in a target project: what to commit, `.gitignore`, test harness, CI |
| `docs/design-rationale.md` | Problem, goals, non-goals, alternatives, risks; for humans deciding on the skill, not loaded by agents running it |
| `docs/images/` | README diagrams, hand-written SVG; `workflow.svg` mirrors the steps of `SKILL.md`, so change them together. Use generic font stacks only: GitHub shows them through `<img>` |
| `references/svg-conventions.md` | How to draw and name the files (steps 3 and 5) |
| `references/platforms.md` | Per-target units, states, layout, capture, tests |
| `scripts/build_doc.py` | Generates the design doc; Python 3.8+ standard library only, no dependencies |
| `scripts/guardrails.py` | Locks approved files and guardrails, checks them unchanged and complete; same constraints |
| `examples/blueprint/` | Worked example; must build cleanly and render correctly. It has approved units but deliberately no `guardrails.lock` and no `_build/clean/` in git, so `check` on it reports them as not locked |
| `LESSONS.md` | Proposed rule changes from real use |
| `CHANGELOG.md` | One entry per change that affects behaviour |

## Changing the skill

- Write for an agent reader: positive instructions, one meaning in one place, a done-when criterion on every step. The `writing-for-agents` skill is the style reference when it is available.
- Rule changes come from real use. Record the case in `LESSONS.md` first; fold it into `SKILL.md` or `references/` only after the user agrees, then mark the entry `folded`.
- The guardrail rule in steps 6 and 7 is a user requirement: tests derived from the approved design exist before a unit's implementation, each fails against the stub, and none is edited to fit the code; a wrong guardrail is a design question for the user. The agent's own tests during implementation follow `/tdd` and are not front-loaded. Keep both halves intact when editing nearby text.
- Keep the version in `CHANGELOG.md`: a `-dev` suffix while work is in progress; the user's commit finalizes it.
- Files are English. This repository is public: no hostnames, internal paths, names or credentials from any user's environment, in examples included.

## Checking a change

1. `python scripts/build_doc.py examples/blueprint` exits 0 (it exits 1 on any warning).
2. Open `examples/blueprint/index.html` (or serve the folder) and look at it in light and dark mode: every state renders, screens show the placed components without their annotations, labels do not overlap.
3. If `build_doc.py` changed, confirm `_build/clean/` copies carry no `annotation` or `context` groups. If `guardrails.py` changed, copy the example into a scratch project and, from its root, confirm `check` lists the approved units' `spec.md` and SVGs as not locked, passes after locking them, fails after editing `spec.md` or deleting a locked file, and reports the screen as changed after editing a button drawing it places.
4. Re-read the changed step of `SKILL.md` as an agent seeing it for the first time: can it tell when the step is done?
