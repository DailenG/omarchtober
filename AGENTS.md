# Omarchtober Agent Instructions

## Invariants

- Preserve the Omarchy plugin ID `dailen.omarchtober` across manifest and QML entry points.
- Keep runtime network-free, dependency-free at the Python package level, and unprivileged.
- Reuse the single configuration normalizer, visual player, QML presenter, scene catalog, and audio engine.
- Keep Fun mode a genuine content-safety boundary: no blood, gore, exposed remains, zombies, threatening faces, weapons, pursuit, or jump scares in bundled art or audio.
- Use original Halloween archetypes. Never reproduce identifiable film characters, masks, houses, music, dialogue, logos, or branded scene names.
- Keep scene art bundled locally as 2560×1440 WebP plates; never generate or download art at runtime.
- Keep presentation non-destructive: paired full-frame crossfades, an optional bounded camera sweep, authored parallax layers, and theme overlay act on the stage, not on base plates.
- Real parallax layers must be same-canvas transparent WebP assets declared by a bounded local manifest. `art.motion: 0` and `art.parallax: 0` must reproduce the base plate exactly.
- Bound configuration input, rotation interval, motion multiplier, media file input, subprocesses, and caches.
- Never edit `/usr/share/omarchy`; it is read-only reference material.
- Preserve the `org.omarchy.screensaver` identity, multi-monitor sibling teardown, and Omarchy-owned lock behavior.

## Scene changes

Read `docs/SCENE_AUTHORING.md`. A new scene is one bundled asset, one runtime key, one player mapping, one catalog entry, one settings entry, behavioral tests, and matching documentation. Do not create alternate infrastructure.

## Verification

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile omarchtober/*.py scripts/omarchtober.py scripts/visual-player.py
python3 scripts/omarchtober.py --check-config >/dev/null
python3 scripts/omarchtober.py --list-scenes
bash -n scripts/launch-omarchtober scripts/idle-integration scripts/select-media
omarchy plugin validate .
/usr/lib/qt6/bin/qmllint visual/Screensaver.qml
/usr/lib/qt6/bin/qmllint -I "$OMARCHY_PATH/shell" Service.qml Config.qml
```

QML metadata warnings for `PanelWindow` and `QProcess::ExitStatus` are expected when `qmllint` exits successfully. New warnings are not.
