"""Public scene contract used by built-in and contributed scenes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..rendering import FrameBuffer, RGB, SceneInfo


class Scene(ABC):
    """A deterministic, resize-aware terminal scene."""

    info: SceneInfo

    def __init__(self, width: int, height: int, config: dict[str, Any], seed: int) -> None:
        self.width = width
        self.height = height
        self.config = config
        self.seed = seed
        self.elapsed = 0.0

    @property
    @abstractmethod
    def background(self) -> RGB:
        """Terminal background color used while the scene is active."""

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def update(self, delta: float) -> None:
        speed = float(self.config["elements"]["animationSpeed"])
        self.elapsed += max(0.0, min(delta, 0.25)) * speed

    @abstractmethod
    def render(self) -> FrameBuffer:
        """Render the current scene state."""
