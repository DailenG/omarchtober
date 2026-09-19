#!/usr/bin/env python3
"""Launch the GPU-backed Omarchtober visual scene player."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

PLUGIN_DIR = Path(__file__).resolve().parent.parent
if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))

from omarchtober.audio import AudioEngine
from omarchtober.config import CONFIG_PATH, load_config

SCENE_FILES = {
    "haunted_estate": "haunted-estate.webp",
    "witching_woods": "witching-woods.webp",
    "pumpkin_hollow": "pumpkin-hollow.webp",
    "midnight_mausoleum": "midnight-mausoleum.webp",
}

PARALLAX_ROOT = PLUGIN_DIR / "assets" / "parallax"
MOTION_ROOT = PLUGIN_DIR / "assets" / "motion"


def scene_layers(paths: list[Path]) -> list[list[dict[str, Any]]]:
    root = PARALLAX_ROOT.resolve()
    all_layers: list[list[dict[str, Any]]] = []
    for path in paths:
        metadata_path = root / path.stem / "layers.json"
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            all_layers.append([])
            continue
        entries = metadata.get("layers") if isinstance(metadata, dict) else []
        layers: list[dict[str, Any]] = []
        if not isinstance(entries, list):
            all_layers.append(layers)
            continue
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("file"), str):
                continue
            source = (metadata_path.parent / entry["file"]).resolve()
            if not source.is_relative_to(root) or not source.is_file():
                continue
            try:
                depth = max(0.0, min(2.0, float(entry.get("depth", 1.0))))
                x_amplitude = max(0.0, min(96.0, float(entry.get("xAmplitude", 0.0))))
                y_amplitude = max(0.0, min(96.0, float(entry.get("yAmplitude", 0.0))))
                opacity = max(0.0, min(1.0, float(entry.get("opacity", 0.5))))
            except (TypeError, ValueError):
                continue
            layers.append(
                {
                    "source": str(source),
                    "depth": depth,
                    "xAmplitude": x_amplitude,
                    "yAmplitude": y_amplitude,
                    "opacity": opacity,
                }
            )
        all_layers.append(layers)
    return all_layers


def scene_lights(paths: list[Path]) -> list[list[dict[str, Any]]]:
    all_lights: list[list[dict[str, Any]]] = []
    for path in paths:
        metadata_path = MOTION_ROOT / path.stem / "lights.json"
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            all_lights.append([])
            continue
        entries = metadata.get("lights") if isinstance(metadata, dict) else []
        lights: list[dict[str, Any]] = []
        if isinstance(entries, list):
            for entry in entries[:24]:
                if not isinstance(entry, dict):
                    continue
                try:
                    light = {
                        "x": max(0.0, min(1.0, float(entry["x"]))),
                        "y": max(0.0, min(1.0, float(entry["y"]))),
                        "radius": max(0.004, min(0.12, float(entry["radius"]))),
                        "intensity": max(0.0, min(0.6, float(entry["intensity"]))),
                        "period": int(max(1800, min(12000, float(entry["period"])))),
                    }
                except (KeyError, TypeError, ValueError):
                    continue
                lights.append(light)
        all_lights.append(lights)
    return all_lights


def scene_paths(config: dict[str, Any]) -> list[Path]:
    experience = config["experience"]
    selected = experience["scene"]
    if selected != "rotation":
        return [PLUGIN_DIR / "assets" / "scenes" / SCENE_FILES[selected]]
    enabled = experience["enabledScenes"]
    paths = [PLUGIN_DIR / "assets" / "scenes" / SCENE_FILES[key] for key in enabled if key in SCENE_FILES]
    return paths or [PLUGIN_DIR / "assets" / "scenes" / SCENE_FILES["haunted_estate"]]


def session_dir() -> Path:
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    if runtime:
        return Path(runtime) / "omarchtober"
    cache = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(cache) / "omarchtober"


def write_session(config: dict[str, Any], paths: list[Path]) -> Path:
    directory = session_dir()
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    payload = {
        "scenes": [str(path) for path in paths],
        "layers": scene_layers(paths),
        "lights": scene_lights(paths),
        "duration": config["experience"]["rotationSeconds"],
        "theme": config["art"]["theme"],
        "motion": config["art"]["motion"],
        "parallaxDepth": config["art"]["parallax"],
        "exitOnMotion": config["integration"]["exitOnPointerMotion"],
    }
    target = directory / "session.json"
    handle, temporary = tempfile.mkstemp(dir=directory, prefix=".session-", suffix=".json")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        json.dump(payload, stream)
    os.chmod(temporary, 0o600)
    os.replace(temporary, target)
    return target


def stop_visual_players() -> None:
    subprocess.run(
        ["pkill", "-f", "[q]ml6.*Screensaver.qml"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def run(config: dict[str, Any], sound_override: bool | None) -> int:
    paths = scene_paths(config)
    missing = [path for path in paths if not path.is_file()]
    if missing:
        print(f"omarchtober: missing scene asset: {missing[0]}", file=sys.stderr)
        return 2

    write_session(config, paths)
    command = ["qml6", "-f", str(PLUGIN_DIR / "visual" / "Screensaver.qml")]

    audio = AudioEngine(config)
    sound_enabled = config["sound"]["enabled"] if sound_override is None else sound_override
    child: subprocess.Popen[bytes] | None = None
    stopping = False

    def stop_handler(_signum: int, _frame: Any) -> None:
        nonlocal stopping
        stopping = True
        if child and child.poll() is None:
            child.terminate()

    previous_handlers = {
        sig: signal.signal(sig, stop_handler)
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT)
    }
    try:
        if sound_enabled:
            audio.start()
        environment = dict(os.environ)
        environment["QML_XHR_ALLOW_FILE_READ"] = "1"
        child = subprocess.Popen(command, cwd=PLUGIN_DIR, env=environment)
        return_code = child.wait()
    finally:
        audio.close()
        for sig, handler in previous_handlers.items():
            signal.signal(sig, handler)
        if not stopping:
            stop_visual_players()
    return return_code


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Omarchtober visual screensaver")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument(
        "--identity",
        default="org.omarchy.screensaver",
        help="argv marker used by Omarchy's screensaver start and stop contract",
    )
    sound = parser.add_mutually_exclusive_group()
    sound.add_argument("--sound", action="store_true")
    sound.add_argument("--no-sound", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = load_config(args.config)
    override = True if args.sound else False if args.no_sound else None
    return run(config, override)


if __name__ == "__main__":
    raise SystemExit(main())
