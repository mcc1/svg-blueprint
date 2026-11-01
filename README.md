# svg-blueprint

An agent skill for designing any user interface (game HUDs and menus, mobile and desktop apps, web) as SVG before writing UI code, and holding the implementation to that design.

SVG is text the agent can write and diff, and a picture the human can look at. That makes it a shared language between the two: the agent draws, the human approves, and the approved drawing becomes the spec that tests are written from and the implementation is checked against. It helps most where there is no standard component library to lean on, such as game UI and custom native controls.

The workflow is component-first, and nothing is implemented until its whole slice (a screen and the components it uses) is approved:

1. **Inventory** every screen, the components each one uses, and every state of each component.
2. **Tokens**: palette, type scale, spacing.
3. **States**: one SVG per component state; behaviour drawn as state frames joined by labelled arrows.
4. **Approval**: the human approves each unit on its own; approved units are locked, and changing one is an explicit reopen.
5. **Screens**: composed only from approved components, at the resolutions where the layout changes, plus the flow between screens.
6. **Guardrails**: tests derived from the approved states, transitions and look, written before the unit is implemented, each failing against a stub, then locked together with the drawings.
7. **Implement**: test-driven, with the agent's own tests; the guardrails must pass without being edited. A guardrail that looks wrong is a design question for the human, not something to patch.
8. **Verify**: screenshots of the real UI next to each approved state.

Drawing whole-screen mockups first tends to fail: palette, layout, component shape and states arrive in one picture that can only be accepted or rejected as a whole. Approving small pieces first keeps every decision small and stable.

The approach was inspired by the idea of letting an AI draw a UI in SVG before writing native or game UI code, where it has little training data to lean on. This skill extends it to component-level approval and implementation checks.

## Install

The repository root is the skill folder. For Claude Code, link or copy it into your skills directory:

```bash
git clone https://github.com/mcc1/svg-blueprint ~/.claude/skills/svg-blueprint
```

Step 7 works best with the [`tdd`](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd) skill installed alongside this one; without it, the agent follows the same red-green-refactor cycle described in `SKILL.md`.

Why guardrails: an agent that writes tests alongside its own code tends to write tests its code passes, and a wrong test then reinforces the wrong choice. Guardrails come from the design, before the code exists, and `scripts/guardrails.py` makes any later edit to them visible.

The design-doc generator needs Python 3.8+ and nothing else:

```bash
python scripts/build_doc.py examples/blueprint
```

Then open `examples/blueprint/index.html`.

## Layout

| Path | Purpose |
|---|---|
| `SKILL.md` | The workflow the agent follows |
| `references/spec-format.md` | Format of each unit's `spec.md` (contract) and `log.md` (history), and of `inventory.md` |
| `references/project-setup.md` | Setup in a target project: what to commit, `.gitignore`, test harness, CI |
| `docs/design-rationale.md` | Why the skill works this way: goals, non-goals, alternatives, risks |
| `references/svg-conventions.md` | Rules for drawing and naming the SVG files |
| `references/platforms.md` | Units, states, layout, capture and test tools per target (games, apps, web, terminal) |
| `AGENTS.md` | Guide for agents changing this skill |
| `scripts/build_doc.py` | Generates the design doc from a blueprint folder |
| `scripts/guardrails.py` | Locks approved drawings and guardrail tests; checks they stay unchanged (a screen counts as changed when a component it places changes) and that nothing approved is left unlocked |
| `examples/blueprint/` | A small worked example: tokens, one button, one dialog screen. Deliberately not locked |
| `LESSONS.md` | Lessons from real use, folded into the skill once agreed |

## Status

Early draft, being sharpened on a real project. Expect the conventions to change.

## License

MIT, see [LICENSE](LICENSE).
