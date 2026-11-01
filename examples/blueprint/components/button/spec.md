---
status: approved
approved: 2026-11-01
size: 120x36
unit: px
---
## Purpose

Primary action button. Example component for the svg-blueprint skill; web target, pointer and keyboard input.

## States

| state | looks like | notes |
|---|---|---|
| default | accent body, label "Confirm" | |
| hover | accent-hover body | |
| pressed | accent-pressed body | while the pointer is held |
| focus | default look plus 2px focus ring | ring sits 3px outside the body, so the file is 126x42 with viewBox starting at -3 |
| disabled | muted body and label | no hover, no focus, no click |

Not applicable: loading (no async action in the example), overflow (the label is fixed text), stretched (fixed size).

## Transitions

| from | to | trigger | timing |
|---|---|---|---|
| default | hover | pointer enter | 120ms ease-out |
| hover | default | pointer leave | 120ms ease-out |
| hover | pressed | pointer down | - |
| pressed | hover | pointer up, fires click | - |
| default | focus | Tab | - |

## Variants

None: fixed size, fixed label, no animation frames.

## Interface

Web component, stack-neutral wording.

- Inputs: `label: string`, `disabled: boolean`.
- Triggers: pointer enter, leave, down and up are pointer events on part `body`; Tab moves keyboard focus to the button.
- Hooks: each SVG part id (`body`, `label`, `focus-ring`) is exposed as `data-testid`.

## Guardrails

Stack-neutral wording; a real project writes them in its own test runner under its guardrail folder and locks them with `scripts/guardrails.py`.

| guardrail | covers | file |
|---|---|---|
| button / default shows label "Confirm" in part `label` on accent body | state default | (example) |
| button / pointer enter switches body to accent-hover | transition default → hover, state hover | (example) |
| button / pointer leave returns body to accent | transition hover → default | (example) |
| button / pointer down switches body to accent-pressed | transition hover → pressed, state pressed | (example) |
| button / pointer up fires one click and returns to hover | transition pressed → hover | (example) |
| button / Tab shows part `focus-ring` | transition default → focus, state focus | (example) |
| button / disabled shows muted body and ignores click | state disabled | (example) |
| button / disabled shows muted body and stays muted on pointer enter | state disabled | (example) |
| button / visual matches each state file, tolerance 1% pixels | files default, hover, pressed, focus, disabled | (example) |

Every guardrail asserts something the stub cannot satisfy, including the disabled ones, so each one fails before implementation.
