---
status: review
size: 320x140
unit: px
---
## Purpose

Composition example: the approved `button` placed with `<image>`, right-aligned with 16px padding.

## States

| state | looks like | notes |
|---|---|---|
| default | title, body text, Confirm button | button receives initial focus |

## Transitions

Single state; none.

## Variants

Reference resolution only; the dialog has a fixed size.

## Interface

- Inputs: `open: boolean`.
- Triggers: setting `open` to true opens the dialog.
- Hooks: parts `title`, `body` and the placed button are exposed as `data-testid`.

## Guardrails

| guardrail | covers | file |
|---|---|---|
| confirm-dialog / opening shows title, body and button | state default | (example) |
| confirm-dialog / button has initial focus on open | state default | (example) |
| confirm-dialog / visual matches default.svg, tolerance 1% pixels | file default.svg | (example) |
