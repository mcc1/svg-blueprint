# Design rationale

Why svg-blueprint works the way it does. This file is for people deciding whether to use or change the skill; agents running the skill do not need it.

## Problem

When an agent builds UI from a prose request, the user only finds out what the agent understood once code exists. Every correction then costs an implementation round, and the agent's own tests, written beside its code, tend to confirm what it built rather than what was meant. The gap is widest where there is no standard component library to anchor both sides: game HUDs and menus, custom native controls, pixel-art interfaces.

## Goals

- The user approves pictures, one small unit at a time, before any UI code is written.
- The approved pictures are precise enough to derive tests from.
- Those tests are fixed before implementation, so the implementation is held to the design rather than the reverse.

## Non-goals

- Producing production assets. Sprites, icons and illustrations stay assets; the blueprint fixes where they go and how they behave.
- Replacing a design tool for a human designer. The blueprint is a communication format between a user and an agent.
- Fixing the implementation's structure. The blueprint fixes the visual result; layout code uses the target platform's idioms.
- Pixel-perfect rendering parity. Fonts and anti-aliasing differ between renderers; visual checks use a tolerance and the user's eye.

## Alternatives considered

| Alternative | Why not the default |
|---|---|
| Prose specification | The user cannot see it; misunderstandings surface only in code |
| Whole-screen mockup first | Mixes palette, spacing, component shape, states and layout into one picture that can only be accepted or rejected as a whole |
| HTML/CSS prototype or a component workbench | Close to final code for web, but web-only, and invites copying prototype code into the product. A good choice for web-only projects that already have a design system |
| Design tool files (for example Figma) | The agent cannot read or edit them reliably as text; diffs are not reviewable |
| Live code prototypes | Each correction is an implementation round; the design decision and the code decision arrive together |
| Tests written alongside the code | Tests drift toward what the code does; a wrong test reinforces the wrong choice |

SVG is text the agent can write and diff, renders in every browser, and is independent of the target platform.

## Risks and limits

- SVG shows an approximation: real font metrics, native controls and engine rendering can differ. Mitigation: overflow states with real text, the font noted in `spec.md`, screenshot comparison in step 8.
- The agent may draw poorly, especially detailed pixel art. Mitigation: small units, alternatives side by side, and assets staying assets.
- Large screens cost context when the agent reads their SVG. Mitigation: screens place components by reference instead of redrawing them.
- The process depends on the user reviewing each unit. Approval is explicit and recorded; nothing is implemented from an unapproved unit.
- The lock makes edits to guardrails visible; it cannot make them impossible. It relies on `guardrails.lock` being committed and its diffs being reviewed.
