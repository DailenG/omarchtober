"""Built-in Omarchtober scene registry."""

from __future__ import annotations

from typing import Any

from .base import Scene
from .haunted_estate import HauntedEstateScene

SCENE_TYPES: dict[str, type[Scene]] = {
    HauntedEstateScene.info.key: HauntedEstateScene,
}


def create_scene(width: int, height: int, config: dict[str, Any], seed: int) -> Scene:
    key = config["experience"]["scene"]
    scene_type = SCENE_TYPES.get(key, HauntedEstateScene)
    return scene_type(width, height, config, seed)


def scene_keys() -> tuple[str, ...]:
    return tuple(SCENE_TYPES)
