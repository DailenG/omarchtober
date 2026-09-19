# Omarchtober

[![CI](https://img.shields.io/github/actions/workflow/status/DailenG/omarchtober/ci.yml?branch=main&style=flat-square&label=tests)](https://github.com/DailenG/omarchtober/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-ef813c?style=flat-square)](LICENSE)
[![Omarchy Quattro](https://img.shields.io/badge/Omarchy-Quattro-c4a3d2?style=flat-square)](https://omarchy.org/)

A living collection of illustrated Halloween nights for Omarchy. Omarchtober fills every monitor with authored, high-resolution dioramas inspired by ANSI engraving, Braille dithering, moonlit pixel art, and antique storybook plates.

**[Website](https://daileng.github.io/omarchtober/)** · **[Scene authoring](docs/SCENE_AUTHORING.md)** · **[Architecture](docs/ARCHITECTURE.md)** · **[Configuration](docs/CONFIGURATION.md)**

<p align="center">
  <img src="preview.png" alt="Four Omarchtober illustrated scenes" width="100%" />
</p>

## The collection

- **Haunted Estate** — a Victorian manor, graveyard, old trees, cats, and lantern-bearing visitors.
- **Witching Woods** — an ancient path, stone well, crooked cottage, mushrooms, owls, and drifting mist.
- **Pumpkin Hollow** — a warm harvest village with a clock tower, pumpkin fields, cottages, and costumed visitors.
- **Midnight Mausoleum** — a cypress-lined cemetery avenue with reflecting pools, statues, fog, and an ornate chapel.

Every scene shares one visual language: midnight navy, ivory moonlight, lavender engraving, warm amber lamps, dense stippling, and layered theatrical depth.

## Features

- GPU-rendered 16:9 artwork with full-frame multi-monitor presentation.
- Moonlit, Harvest, Spectral, and Midnight color treatments.
- Full-frame presentation: the complete 16:9 illustration is never stretched or cropped.
- Adjustable multi-plane atmosphere: mist, flying silhouettes, lantern motes, and storm light move independently over the static plate.
- Haunted Estate adds two source-derived, feathered high-resolution depth layers with a dedicated Parallax Depth control; `0` restores the exact static composition.
- Configurable master motion, parallax depth, atmosphere layers, and scene duration.
- Optional locally synthesized ambience or user-selected local media.
- Tray control, idle integration, pointer/key dismissal, and unchanged Omarchy lock ownership.
- Runtime network-free, unprivileged, and dependency-free at the Python package level.

## Install

```bash
omarchy plugin add https://github.com/DailenG/omarchtober --enable
```

The pumpkin icon appears in the system tray. Click it to open the Visual Collection, middle-click to start, or use:

```bash
omarchy-shell omarchtober configure
omarchy-shell omarchtober start
omarchy-shell omarchtober stop
```

Any key or click returns to the desktop. Pointer motion also dismisses when enabled.

## Configuration

Settings are written atomically to:

```text
~/.config/omarchtober/config.json
```

The control room selects the scene or complete rotation, theme, full-frame presentation, master motion, Parallax Depth, four independent atmosphere layers, scene duration, ambience, idle launch, and dismissal behavior. Version-one terminal through version-three visual configurations migrate safely.

Diagnostics:

```bash
python3 scripts/omarchtober.py --check-config
python3 scripts/omarchtober.py --list-scenes
python3 scripts/omarchtober.py --audio-test 8
```

## Runtime

`qml6` presents the scene assets through Qt Quick with `PreserveAspectFit`, so the complete authored 16:9 composition remains intact on every display. Paired base-plate and parallax-layer stacks crossfade as one scene, without reconstructing the artwork. Haunted Estate supplies transparent, full-resolution feathered canopy and grounds layers that drift at distinct manifest-defined depths over its base plate; setting Parallax Depth to `0` hides both. Distant flying silhouettes, midground fog, foreground lantern motes, and storm light move at separate rates for additional depth. The launcher opens one fullscreen player on each monitor and preserves Omarchy's existing idle and lock lifecycle.

No runtime image generation, downloads, browser engine, remote assets, or privileged writes.

## Create a scene

Read [Scene Authoring](docs/SCENE_AUTHORING.md). New work must be an original 16:9 companion plate, visually coherent with the collection, safe in Fun mode, free of copied characters and architecture, and bundled locally as a compressed WebP asset.

## Development

```bash
git clone https://github.com/DailenG/omarchtober
cd omarchtober
python3 -m unittest discover -s tests -v
python3 -m py_compile omarchtober/*.py scripts/omarchtober.py scripts/visual-player.py
bash -n scripts/launch-omarchtober scripts/idle-integration scripts/select-media
omarchy plugin validate .
/usr/lib/qt6/bin/qmllint visual/Screensaver.qml
/usr/lib/qt6/bin/qmllint -I "$OMARCHY_PATH/shell" Service.qml Config.qml
```

Live setup and pull-request expectations are in [CONTRIBUTING.md](CONTRIBUTING.md). Trust boundaries are documented in [Security](SECURITY.md).

## License

MIT © 2026 Dailen Gunter.
