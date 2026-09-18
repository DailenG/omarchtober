"""Configuration loading and normalization for Omarchtober."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

PLUGIN_DIR = Path(__file__).resolve().parent.parent
DEFAULTS_PATH = PLUGIN_DIR / "defaults.json"
CONFIG_PATH = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "omarchtober" / "config.json"
MAX_CONFIG_BYTES = 256 * 1024
MAX_TERMINAL_COLUMNS = 500
MAX_TERMINAL_LINES = 200
IMPLEMENTED_SCENES = {"haunted_estate"}
PALETTES = {"moonlit", "harvest", "spectral", "monochrome"}
MEDIA_EXTENSIONS = {".mp3", ".mp4", ".m4a", ".ogg", ".opus", ".flac", ".wav", ".webm"}
MAX_MEDIA_BYTES = 2 * 1024 * 1024 * 1024


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.stat().st_size > MAX_CONFIG_BYTES:
            return copy.deepcopy(fallback)
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return copy.deepcopy(fallback)


def _number(value: Any, low: float, high: float, fallback: float) -> float:
    if isinstance(value, bool):
        return fallback
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    if number != number or number in (float("inf"), float("-inf")):
        return fallback
    return max(low, min(high, number))


def _boolean(value: Any, fallback: bool) -> bool:
    return value if isinstance(value, bool) else fallback


def defaults() -> dict[str, Any]:
    loaded = _read_json(DEFAULTS_PATH, {})
    if not isinstance(loaded, dict):
        raise RuntimeError("packaged defaults.json must contain an object")
    return loaded


def normalize_config(raw: Any) -> dict[str, Any]:
    base = defaults()
    incoming = raw if isinstance(raw, dict) else {}
    result = copy.deepcopy(base)

    experience = incoming.get("experience") if isinstance(incoming.get("experience"), dict) else {}
    mode = str(experience.get("mode", base["experience"]["mode"]))
    scene = str(experience.get("scene", base["experience"]["scene"]))
    result["experience"]["mode"] = mode if mode in {"fun", "scary"} else base["experience"]["mode"]
    result["experience"]["scene"] = scene if scene in IMPLEMENTED_SCENES else base["experience"]["scene"]

    elements = incoming.get("elements") if isinstance(incoming.get("elements"), dict) else {}
    limits = {
        "stars": (0, 160),
        "clouds": (0, 12),
        "bats": (0, 40),
        "gravestones": (0, 36),
        "apparitions": (0, 12),
        "wanderers": (0, 10),
        "pumpkins": (0, 24),
        "lightning": (0, 100),
    }
    for key, (low, high) in limits.items():
        result["elements"][key] = round(_number(elements.get(key), low, high, base["elements"][key]))
    result["elements"]["animationSpeed"] = round(
        _number(elements.get("animationSpeed"), 0.25, 2.0, base["elements"]["animationSpeed"]), 2
    )

    art = incoming.get("art") if isinstance(incoming.get("art"), dict) else {}
    palette = str(art.get("palette", base["art"]["palette"]))
    result["art"]["palette"] = palette if palette in PALETTES else base["art"]["palette"]
    result["art"]["showStatus"] = _boolean(art.get("showStatus"), base["art"]["showStatus"])

    sound = incoming.get("sound") if isinstance(incoming.get("sound"), dict) else {}
    result["sound"]["enabled"] = _boolean(sound.get("enabled"), base["sound"]["enabled"])
    result["sound"]["volume"] = round(_number(sound.get("volume"), 0, 100, base["sound"]["volume"]))
    source = str(sound.get("source", base["sound"]["source"]))
    result["sound"]["source"] = source if source in {"procedural", "media"} else base["sound"]["source"]
    media_path = sound.get("mediaPath", base["sound"]["mediaPath"])
    result["sound"]["mediaPath"] = media_path if isinstance(media_path, str) and len(media_path) <= 4096 else ""
    for key in ("wind", "thunder", "creatures"):
        result["sound"][key] = _boolean(sound.get(key), base["sound"][key])

    integration = incoming.get("integration") if isinstance(incoming.get("integration"), dict) else {}
    result["integration"]["idleEnabled"] = _boolean(
        integration.get("idleEnabled"), base["integration"]["idleEnabled"]
    )
    result["integration"]["exitOnPointerMotion"] = _boolean(
        integration.get("exitOnPointerMotion"), base["integration"]["exitOnPointerMotion"]
    )
    return result


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    return normalize_config(_read_json(path, {}))


def clamp_dimensions(width: int, height: int) -> tuple[int, int]:
    return (
        max(40, min(MAX_TERMINAL_COLUMNS, int(width))),
        max(16, min(MAX_TERMINAL_LINES, int(height))),
    )


def validate_media_path(value: str) -> tuple[Path | None, str]:
    if not value:
        return None, "no custom media selected"
    try:
        path = Path(value)
        if not path.is_absolute():
            return None, "custom media path must be absolute"
        if path.is_symlink():
            return None, "custom media must not be a symbolic link"
        resolved = path.resolve(strict=True)
        stat = resolved.stat()
    except (OSError, RuntimeError):
        return None, "custom media file is unavailable"
    if not resolved.is_file():
        return None, "custom media must be a regular file"
    if resolved.suffix.lower() not in MEDIA_EXTENSIONS:
        return None, "unsupported custom media format"
    if stat.st_size > MAX_MEDIA_BYTES:
        return None, "custom media exceeds the 2 GiB limit"
    return resolved, ""
