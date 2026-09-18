# Contributing

Contributions must preserve four invariants: Fun mode is genuinely family-friendly, runtime is network-free and unprivileged, Omarchy retains lock ownership, and configured populations remain exact.

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

Read `docs/SCENE_AUTHORING.md` and `AGENTS.md`. New scenes must be original, deterministic, mode-safe, adaptive, and complete. Do not reproduce branded characters, masks, locations, music, dialogue, or logos.

## Code boundaries

- Keep Python 3.11 compatibility and no third-party Python packages.
- Avoid per-frame subprocesses, file reads, unbounded collections, or avoidable entity recreation.
- Preserve the 256 KiB configuration and 500×200 frame ceilings.
- Preserve keyboard, click, pointer-motion, signal, and terminal-mode cleanup.
- Keep one audio leader and no-follow private locks.
- Never modify `/usr/share/omarchy` or user-owned toggle state.
- Keep `manifest.json`, `Service.qml`, and `Config.qml` IDs identical.

## Verification

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile omarchtober/*.py omarchtober/scenes/*.py scripts/omarchtober.py
python3 scripts/omarchtober.py --snapshot --width 120 --height 36 --seed 7 >/dev/null
python3 scripts/omarchtober.py --snapshot --width 200 --height 52 --seed 7 >/dev/null
python3 scripts/omarchtober.py --check-config >/dev/null
bash -n scripts/launch-omarchtober scripts/idle-integration scripts/select-media
omarchy plugin validate .
/usr/lib/qt6/bin/qmllint -I "$OMARCHY_PATH/shell" Service.qml Config.qml
```

QML metadata warnings for `PanelWindow` and `QProcess::ExitStatus` are expected when lint exits successfully. Exercise the actual control room before submitting visual changes.

## Pull requests

Include the observable change, design decision, deterministic snapshot or capture, exact verification commands and results, mode-safety impact, and documentation updates. Keep each pull request focused.

Contributions are licensed under the MIT License.
