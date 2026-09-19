# Contributing

Contributions must preserve four invariants: Fun mode is genuinely family-friendly, runtime is network-free and unprivileged, Omarchy retains lock ownership, and scene art stays bundled and authored rather than generated at runtime.

## Development

```bash
git clone https://github.com/DailenG/omarchtober
cd omarchtober
python3 -m unittest discover -s tests -v
omarchy plugin validate .
```

For a live development copy:

```bash
PLUGIN_ID=dailen.omarchtober
PLUGIN_DIR="$HOME/.config/omarchy/plugins/$PLUGIN_ID"
mkdir -p "$PLUGIN_DIR"
cp -a --no-preserve=ownership ./. "$PLUGIN_DIR/"
omarchy plugin enable "$PLUGIN_ID"
```

Files hot-reload. Run `omarchy-shell shell rescanPlugins` only when discovery does not update.

## Scene work

Read `docs/SCENE_AUTHORING.md` and `AGENTS.md`. New plates must be original, visually coherent with the collection, family-safe, 2560×1440 WebP, and committed locally. Do not reproduce branded characters, masks, locations, music, dialogue, or logos.

## Code boundaries

- Keep Python 3.11 compatibility and no third-party Python packages.
- Keep the presentation pipeline non-destructive and free of per-frame subprocesses or file reads.
- Preserve the 256 KiB configuration cap, 15–900 second rotation range, and 0–2 motion range.
- Preserve key, click, wheel, pointer-motion, signal, and sibling-teardown behavior.
- Keep one audio leader and no-follow private locks.
- Never modify `/usr/share/omarchy` or user-owned toggle state.
- Keep `manifest.json`, `Service.qml`, and `Config.qml` IDs identical.

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

QML metadata warnings for `PanelWindow` and `QProcess::ExitStatus` are expected when lint exits successfully. Exercise the actual fullscreen player and control room before submitting visual changes.

## Pull requests

Include the observable change, design decision, screenshot or capture, exact verification commands and results, content-safety impact, and documentation updates. Keep each pull request focused.

Contributions are licensed under the MIT License.
