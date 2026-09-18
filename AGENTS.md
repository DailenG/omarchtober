# Omarchtober Agent Instructions

## Invariants

- Preserve the Omarchy plugin ID `dailen.omarchtober` across manifest and QML entry points.
- Keep runtime network-free, dependency-free at the Python package level, and unprivileged.
- Reuse the single scene registry, configuration normalizer, terminal loop, dismissal decoder, frame buffer, and audio engine.
- Treat Fun mode as a content-safety boundary: no blood, gore, exposed remains, zombies, threatening skeletons, menacing faces, weapons, pursuit, or jump scares.
- Use original Halloween archetypes. Never reproduce identifiable film characters, masks, houses, music, dialogue, logos, or branded scene names.
- Keep configured entity populations exact across Compact, Standard, Cinematic, and Panoramic layouts.
- Keep deterministic rendering for a fixed config, seed, dimensions, and elapsed time.
- Bound dimensions, populations, configuration input, file input, subprocesses, and caches.
- Never edit `/usr/share/omarchy`; it is read-only reference material.
- Preserve the `org.omarchy.screensaver` window identity and Omarchy-owned lock behavior.

## Scene changes

Read `docs/SCENE_AUTHORING.md`. A new scene is one module, one registry entry, one catalog entry, one settings entry, behavioral tests, and matching user documentation. Do not create alternate infrastructure.

## Verification

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile omarchtober/*.py omarchtober/scenes/*.py scripts/omarchtober.py
python3 scripts/omarchtober.py --snapshot --width 120 --height 36 --seed 7 >/dev/null
python3 scripts/omarchtober.py --snapshot --width 200 --height 52 --seed 7 >/dev/null
bash -n scripts/launch-omarchtober scripts/idle-integration scripts/select-media
omarchy plugin validate .
/usr/lib/qt6/bin/qmllint -I "$OMARCHY_PATH/shell" Service.qml Config.qml
```

QML metadata warnings for `PanelWindow` and `QProcess::ExitStatus` are expected when `qmllint` exits successfully. New warnings are not.
