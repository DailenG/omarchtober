"""Allocation-bounded terminal drawing primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .config import clamp_dimensions

RGB = tuple[int, int, int]


def mix(start: RGB, end: RGB, amount: float) -> RGB:
    amount = max(0.0, min(1.0, amount))
    return tuple(round(left + (right - left) * amount) for left, right in zip(start, end))


class FrameBuffer:
    __slots__ = ("width", "height", "chars", "colours")

    def __init__(self, width: int, height: int, background: str = " ") -> None:
        self.width, self.height = clamp_dimensions(width, height)
        char = background[0] if background else " "
        self.chars = [[char] * self.width for _ in range(self.height)]
        self.colours: list[list[RGB | None]] = [[None] * self.width for _ in range(self.height)]

    def put(self, x: int, y: int, char: str, colour: RGB | None = None) -> None:
        if 0 <= x < self.width and 0 <= y < self.height and char:
            self.chars[y][x] = char[0]
            self.colours[y][x] = colour

    def text(self, x: int, y: int, text: str, colour: RGB | None = None) -> None:
        for offset, char in enumerate(text):
            if char != " ":
                self.put(x + offset, y, char, colour)

    def sprite(self, x: int, y: int, lines: Iterable[str], colour: RGB | None = None) -> None:
        for row, line in enumerate(lines):
            self.text(x, y + row, line, colour)

    def fill(self, y_start: int, y_end: int, char: str, colour: RGB | None = None) -> None:
        for y in range(max(0, y_start), min(self.height, y_end)):
            for x in range(self.width):
                self.put(x, y, char, colour)

    def plain(self) -> str:
        return "\n".join("".join(row).rstrip() for row in self.chars)

    def ansi(self) -> str:
        output: list[str] = ["\x1b[H"]
        current: RGB | None = None
        for y, row in enumerate(self.chars):
            last = self.width - 1
            while last >= 0 and row[last] == " ":
                last -= 1
            for x in range(last + 1):
                colour = self.colours[y][x]
                if colour is not None and colour != current:
                    output.append(f"\x1b[38;2;{colour[0]};{colour[1]};{colour[2]}m")
                    current = colour
                output.append(row[x])
            output.append("\x1b[K")
            if y != self.height - 1:
                output.append("\n")
        output.append("\x1b[0m")
        return "".join(output)


@dataclass(slots=True, frozen=True)
class SceneInfo:
    key: str
    name: str
    description: str
    supports_fun: bool = True
    supports_scary: bool = True
