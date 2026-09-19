# Changelog

All notable changes follow Keep a Changelog. Versions use Semantic Versioning.

## [Unreleased]

### Changed

- Replaced the terminal ANSI renderer with a GPU visual scene player: `scripts/visual-player.py` plus `visual/Screensaver.qml` present bundled 2560×1440 WebP plates fullscreen with full-frame aspect preservation, long crossfades, and theme overlays.
- Reframed the control room as the Visual Collection: scene or full-collection rotation, enabled-scene selection, rotation interval, theme, Estate parallax motion, and parallax controls.
- Migrated configuration to schema version 5 with safe upgrades from versions 1 through 4; retired the generic atmosphere controls rather than layering procedural effects over the authored plates.
- Added a real-parallax asset pack for Haunted Estate: two transparent, source-derived 2560×1440 feathered depth layers plus a validated local multi-layer manifest. Layer stacks now crossfade with their base plates and apply per-layer manifest depth; Parallax Depth `0` retains a pixel-faithful static baseline.
- Rewrote README, architecture, configuration, scene-authoring, roadmap, security, agent instructions, and the project website around the authored visual collection.
- Regenerated the project preview as a four-scene contact sheet.

### Added

- Four bundled scenes: Haunted Estate, Witching Woods, Pumpkin Hollow, and Midnight Mausoleum.

### Removed

- Terminal scene modules, frame buffer, ANSI renderer, adaptive detail tiers, deterministic snapshot CLI, and the SVG previews.


## [0.1.0] - 2026-09-18

### Added

- Omarchy service, tray menu, overlay control room, idle integration, and multi-monitor launcher.
- Haunted Estate scene with moon, clouds, stars, bats, Victorian manor, graveyard, pumpkins, emerging figures, and walkers.
- Global Fun and Scary content modes with visual and procedural-audio substitutions.
- Exact element counts, four color palettes, lightning frequency, animation speed, and optional status text.
- Compact, Standard, Cinematic, and Panoramic detail tiers.
- Optional procedural PipeWire ambience and user-selected local media playback through `mpv`.
- Deterministic snapshots, configuration diagnostics, behavioral tests, scene-authoring contract, and AI-agent prompt.
- GitHub Pages project site and CI workflow.

[Unreleased]: https://github.com/DailenG/omarchtober/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/DailenG/omarchtober/releases/tag/v0.1.0
