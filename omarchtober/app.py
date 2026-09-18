"""Omarchtober command-line renderer."""

from __future__ import annotations

import argparse
import json
import os
import select
import signal
import sys
import time
from pathlib import Path
from typing import Any

from .audio import AudioEngine
from .config import CONFIG_PATH, load_config, validate_media_path
from .scenes import create_scene, scene_keys
from .terminal import DismissalInput, TerminalSession, dismiss_screensaver_windows, terminal_size


def run_interactive(config: dict[str, Any], seed: int, sound_override: bool | None) -> int:
    width, height = terminal_size()
    scene = create_scene(width, height, config, seed)
    audio = AudioEngine(config)
    sound_enabled = config["sound"]["enabled"] if sound_override is None else sound_override
    dismissal = DismissalInput(config["integration"]["exitOnPointerMotion"])
    stop_requested = False
    user_dismissed = False

    def stop_handler(_signum: int, _frame: Any) -> None:
        nonlocal stop_requested
        stop_requested = True

    previous_handlers = {}
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
        previous_handlers[sig] = signal.signal(sig, stop_handler)
    try:
        with TerminalSession(scene.background):
            if sound_enabled:
                audio.start()
            started = time.monotonic()
            previous = started
            next_frame = started
            while not stop_requested:
                now = time.monotonic()
                if dismissal.expired(now):
                    user_dismissed = True
                    break
                if now - started > 0.35 and select.select([sys.stdin], [], [], 0)[0]:
                    if dismissal.feed(os.read(sys.stdin.fileno(), 4096), now):
                        user_dismissed = True
                        break
                new_width, new_height = terminal_size()
                if (new_width, new_height) != (width, height):
                    width, height = new_width, new_height
                    scene.resize(width, height)
                scene.update(now - previous)
                previous = now
                sys.stdout.write(scene.render().ansi())
                sys.stdout.flush()
                next_frame += 1.0 / 24.0
                delay = next_frame - time.monotonic()
                if delay > 0:
                    time.sleep(delay)
                else:
                    next_frame = time.monotonic()
    finally:
        audio.close()
        for sig, handler in previous_handlers.items():
            signal.signal(sig, handler)
    if user_dismissed:
        dismiss_screensaver_windows()
    return 0


def run_audio_test(config: dict[str, Any], seconds: float) -> int:
    if config["sound"]["source"] == "media":
        path, error = validate_media_path(config["sound"]["mediaPath"])
        if error:
            print(f"omarchtober audio test: {error}", file=sys.stderr)
            return 3
        print(f"Testing custom media playback: {path}", file=sys.stderr)
    engine = AudioEngine(config, diagnostic=config["sound"]["source"] == "procedural")
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
    parser = argparse.ArgumentParser(description="Terminal-native Halloween nightscape for Omarchy")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH, help="configuration JSON path")
    parser.add_argument("--seed", type=int, default=None, help="deterministic scene seed")
    parser.add_argument("--snapshot", action="store_true", help="render one plain-text frame and exit")
    parser.add_argument("--width", type=int, default=120, help="snapshot width")
    parser.add_argument("--height", type=int, default=36, help="snapshot height")
    parser.add_argument("--time", type=float, default=3.0, help="snapshot animation time")
    parser.add_argument("--check-config", action="store_true", help="print normalized configuration and exit")
    parser.add_argument("--check-media", action="store_true", help="validate configured custom media and exit")
    parser.add_argument("--list-scenes", action="store_true", help="list registered scene keys and exit")
    parser.add_argument("--audio-test", type=float, nargs="?", const=8.0, default=None, metavar="SECONDS")
    sound = parser.add_mutually_exclusive_group()
    sound.add_argument("--sound", action="store_true", help="enable ambience for this run")
    sound.add_argument("--no-sound", action="store_true", help="disable ambience for this run")
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
        print("\n".join(scene_keys()))
        return 0
    if args.audio_test is not None:
        return run_audio_test(config, args.audio_test)
    seed = args.seed if args.seed is not None else (os.getpid() ^ time.time_ns()) & 0xFFFFFFFF
    if args.snapshot:
        scene = create_scene(args.width, args.height, config, seed)
        scene.update(max(0.0, min(args.time, 3600.0)))
        print(scene.render().plain())
        return 0
    sound_override = True if args.sound else False if args.no_sound else None
    try:
        return run_interactive(config, seed, sound_override)
    except RuntimeError as error:
        print(f"omarchtober: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
