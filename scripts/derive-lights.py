#!/usr/bin/env python3
"""Derive a scene's emissive light manifest from its own bundled plate.

The manifest records where a plate already paints warm lamplight, so the
player can breathe those exact points instead of inventing new elements.
Requires ImageMagick's `magick` binary. Run offline; never at runtime.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent
SCENE_ROOT = PLUGIN_DIR / "assets" / "scenes"
MOTION_ROOT = PLUGIN_DIR / "assets" / "motion"
SAMPLE_WIDTH = 640
SAMPLE_HEIGHT = 360
MAX_LIGHTS = 24


def sample(plate: Path) -> bytes:
    with tempfile.TemporaryDirectory() as directory:
        raw = Path(directory) / "plate.rgb"
        subprocess.run(
            [
                "magick",
                str(plate),
                "-resize",
                f"{SAMPLE_WIDTH}x{SAMPLE_HEIGHT}!",
                "-depth",
                "8",
                f"rgb:{raw}",
            ],
            check=True,
        )
        return raw.read_bytes()


def emissive_points(data: bytes) -> set[tuple[int, int]]:
    points: set[tuple[int, int]] = set()
    for y in range(SAMPLE_HEIGHT):
        row = y * SAMPLE_WIDTH * 3
        for x in range(SAMPLE_WIDTH):
            index = row + x * 3
            red, green, blue = data[index], data[index + 1], data[index + 2]
            if red > 150 and green > 95 and blue < 130 and red - blue > 60:
                points.add((x, y))
    return points


def clusters(points: set[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    found: list[list[tuple[int, int]]] = []
    remaining = set(points)
    while remaining:
        stack = [remaining.pop()]
        group = list(stack)
        while stack:
            cx, cy = stack.pop()
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    neighbour = (cx + dx, cy + dy)
                    if neighbour in remaining:
                        remaining.discard(neighbour)
                        stack.append(neighbour)
                        group.append(neighbour)
        if len(group) >= 4:
            found.append(group)
    found.sort(key=len, reverse=True)
    return found[:MAX_LIGHTS]


def lights(plate: Path) -> list[dict[str, float | int]]:
    groups = clusters(emissive_points(sample(plate)))
    derived: list[dict[str, float | int]] = []
    for index, group in enumerate(groups):
        xs = [point[0] for point in group]
        ys = [point[1] for point in group]
        span = max(max(xs) - min(xs), max(ys) - min(ys))
        radius = min(0.05, max(0.014, (span + 10) / SAMPLE_WIDTH * 1.9 * 0.68))
        strength = min(0.6, 0.18 + len(group) / 420.0)
        derived.append(
            {
                "x": round(sum(xs) / len(xs) / SAMPLE_WIDTH, 4),
                "y": round(sum(ys) / len(ys) / SAMPLE_HEIGHT, 4),
                "radius": round(radius, 4),
                "intensity": round(min(0.3, 0.1 + (strength - 0.18) * 0.55), 3),
                "period": 3200 + ((index * 617) % 4200),
            }
        )
    return derived


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plates", nargs="*", type=Path, help="scene plates; default every bundled plate")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    plates = args.plates or sorted(SCENE_ROOT.glob("*.webp"))
    for plate in plates:
        target = MOTION_ROOT / plate.stem / "lights.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {"lights": lights(plate)}
        target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"{target.relative_to(PLUGIN_DIR)}: {len(payload['lights'])} lights")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
