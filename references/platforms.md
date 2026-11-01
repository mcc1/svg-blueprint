# Platforms

Reference for [`SKILL.md`](../SKILL.md): what changes per target. Read the section for the target before step 1. Tool names below are common starting points, not requirements; use what the project already has, and check a tool's current docs before relying on an API.

Every section answers the same five questions: **units** (what one SVG unit means), **states** (what to add to the inventory), **layout** (what replaces SVG coordinates in step 7), **capture** (how to get `shots/` in step 8), **tests** (where state, transition and visual guardrails run in step 6).

## Games (HUD, menus, in-world UI)

- **Units**: the game's reference resolution. Draw at that resolution in `game px` and state the scaling rule in `spec.md` (integer scale for pixel art, scale-to-fit, scale-with-height). Pixel art: whole pixels only, `shape-rendering="crispEdges"`, and draw at 1x so the doc's zoom shows true pixels.
- **States**: input focus is its own state per input type: mouse hover, gamepad or keyboard focus (the focus ring is part of the design), pressed, and the glyph set per controller when prompts show buttons. Add gameplay-driven states (low health, cooldown, locked, new, unaffordable) and their thresholds. Overlay UI is drawn over a representative backdrop in a `context` group, light and dark scenes both when legibility depends on it.
- **Layout**: anchors and containers of the engine (Godot `Control` anchors and containers; in Unity, UI Toolkit's flexbox layout or uGUI anchors and layout groups; immediate-mode layout in egui or Dear ImGui). Safe areas for TV and handheld.
- **Animation**: drawn as key frames (`<state>.f1.svg`, `.f2`) plus timing in `transitions.svg`; sprite sheets stay assets, the blueprint fixes where and when they play.
- **Capture**: a debug scene or command that shows one component in one state at the reference resolution, captured by the engine (viewport texture to image in Godot, `ScreenCapture` in Unity). Build this scene early; step 6 and step 8 both reuse it. Capture needs a real renderer: Godot's `--headless` mode uses a dummy renderer with nothing to capture, so visual tests run with rendering on (a desktop session or a virtual display in CI).
- **Tests**: keep UI state as logic separate from rendering (a state machine or view model), so state and transition tests run without rendering in the engine's test runner (GUT or gdUnit4 for Godot, Unity Test Framework). Visual tests render the debug scene and compare against the blueprint rendered at the same resolution, with a tolerance.

## Mobile and desktop apps (native)

- **Units**: `pt` (iOS, macOS) or `dp` (Android); desktop toolkits use logical px. Draw at 1x logical size.
- **States**: touch has no hover; add pressed, long-press, and swipe states where used. Add dark mode, dynamic type or the largest font scale, right-to-left when shipped, and keyboard focus on desktop. Minimum touch target belongs in `spec.md`.
- **Layout**: the toolkit's stacks and constraints (SwiftUI stacks, Jetpack Compose rows and columns, Qt layouts, Flutter widgets). Safe areas and notches on screens.
- **Capture**: preview or snapshot tooling of the toolkit, or an emulator or simulator screenshot of a screen showing one state.
- **Tests**: view-model or state tests in the platform's unit-test runner; visual tests with snapshot libraries (swift-snapshot-testing for SwiftUI and UIKit, Paparazzi or Roborazzi for Compose, golden tests in Flutter).

## Web

- **Units**: CSS px at 1x.
- **States**: hover, focus-visible, active, disabled, plus each breakpoint the product supports. Reduced motion when transitions animate.
- **Layout**: flex and grid; the blueprint's breakpoints become media or container queries.
- **Capture**: a component workbench (Storybook, Ladle) or a test page rendering one state, captured by a headless browser.
- **Tests**: component tests in the project's runner. Query by accessible role and name first; parts with no accessible name carry the SVG part id as a test id (Testing Library reads `data-testid` by default, or the attribute set with `configure({ testIdAttribute })`). Visual tests with the browser's screenshot comparison (Playwright `toHaveScreenshot`).

## Terminal UI

- **Units**: character cells. Pick a fixed cell size in SVG units (for example 8 wide by 16 high), state it in `spec.md`, place one `<text>` per row at those coordinates in a monospace font, and size the `viewBox` as columns × 8 by rows × 16.
- **States**: focus, selection, narrow terminal width, no-colour mode.
- **Capture and tests**: render to a buffer and compare text (snapshot of the cell grid) rather than pixels.

## Capturing at 1x

Screenshots in step 8 are taken at 1x so they line up with the drawings. On a HiDPI display set the device scale factor to 1 for the capture (browser device scale factor, simulator scale, engine window scale), or downscale the capture by exactly the scale factor. Many resolutions, languages and frames produce many PNGs: keep `shots/` small by capturing approved states only, and consider Git LFS for large sets.

## Rendering the blueprint for visual tests

Visual tests compare a screenshot with the blueprint, so the SVG has to be rasterized at the implementation's resolution. Rasterize the `_build/clean/` copy of the state, which `build_doc.py` has already flattened and stripped of annotation and context groups; never the source file. Render it with the same engine family as the target where possible (a headless browser for web; any SVG renderer such as resvg or a browser for others), at the reference size. The `_build/clean/` copies have images inlined but not fonts: give the renderer the font files from the Assets table of `inventory.md` (resvg and most renderers take font files or a font folder as options; a headless browser needs a page that declares them with `@font-face`). A text check against a declined font compares against the fallback, so it needs a looser tolerance or the user's agreement to drop it. Compare with a tolerance: font rasterization differs between renderers, so a visual test asserts layout, colour and presence, and the human comparison in step 8 covers the rest.
