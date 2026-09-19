"""Omarchtober configuration and audio diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .audio import AudioEngine
from .config import CONFIG_PATH, SCENES, load_config, validate_media_path


def run_audio_test(config: dict[str, object], seconds: float) -> int:
    sound = config["sound"]
    assert isinstance(sound, dict)
    if sound["source"] == "media":
        path, error = validate_media_path(str(sound["mediaPath"]))
        if error:
            print(f"omarchtober audio test: {error}", file=sys.stderr)
            return 3
        print(f"Testing custom media playback: {path}", file=sys.stderr)
    engine = AudioEngine(config, diagnostic=sound["source"] == "procedural")
    if not engine.start():
        print(f"omarchtober audio test: {engine.last_error}", file=sys.stderr)
        return 3
    try:
        time.sleep(max(0.25, min(seconds, 60.0)))
    finally:
        engine.close()
    print("Omarchtober audio test completed", file=sys.stderr)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visual Halloween scenes for Omarchy")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH, help="configuration JSON path")
    parser.add_argument("--check-config", action="store_true", help="print normalized configuration and exit")
    parser.add_argument("--check-media", action="store_true", help="validate configured custom media and exit")
    parser.add_argument("--list-scenes", action="store_true", help="list bundled scene keys and exit")
    parser.add_argument("--audio-test", type=float, nargs="?", const=8.0, default=None, metavar="SECONDS")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = load_config(args.config)
    if args.check_config:
        print(json.dumps(config, indent=2, sort_keys=True))
        return 0
    if args.check_media:
        path, error = validate_media_path(config["sound"]["mediaPath"])
        if error:
            print(f"omarchtober media check: {error}", file=sys.stderr)
            return 4
        print(f"Omarchtober custom media ready: {path}")
        return 0
    if args.list_scenes:
        print("\n".join(SCENES))
        return 0
    if args.audio_test is not None:
        return run_audio_test(config, args.audio_test)
    print("Use scripts/visual-player.py to launch the screensaver.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
