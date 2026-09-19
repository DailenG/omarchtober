# Changelog

All notable changes follow Keep a Changelog. Versions use Semantic Versioning.

## [Unreleased]

### Changed

- Replaced the terminal ANSI renderer with a GPU visual scene player: `scripts/visual-player.py` plus `visual/Screensaver.qml` present bundled 2560×1440 WebP plates fullscreen with full-frame aspect preservation, long crossfades, theme overlays, and independently animated atmosphere planes.
- Reframed the control room as the Visual Collection: scene or full-collection rotation, enabled-scene selection, rotation interval, theme, master motion, and individual mist, flight, lantern, and storm controls.
- Migrated configuration to schema version 4 with safe upgrades from versions 1 through 3; element counts, palettes, and status text were removed.
- Added an initial real-parallax asset pack for Haunted Estate: a transparent, source-derived 2560×1440 feathered foreground plus a validated local layer manifest. The new Parallax Depth control supports a pixel-faithful zero-depth baseline.
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
