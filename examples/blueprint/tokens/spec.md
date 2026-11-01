---
status: approved
approved: 2026-11-01
unit: px
---
## Purpose

Palette, type scale and spacing for the example; web target.

## Interface

- Theme artefact: CSS custom properties on `:root`, one per token (`--accent`, `--accent-hover`, `--accent-pressed`, `--muted`, `--surface`, `--focus`).
- Hooks: a test reads each property with `getComputedStyle(document.documentElement)`.

## Guardrails

| guardrail | covers | file |
|---|---|---|
| tokens / every colour token in tokens.svg is defined with its value | all colour tokens | (example) |
