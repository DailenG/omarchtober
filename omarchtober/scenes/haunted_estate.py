"""Flagship moonlit Victorian estate scene."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any

from ..config import clamp_dimensions
from ..rendering import FrameBuffer, RGB, SceneInfo, mix
from .base import Scene

PALETTES: dict[str, dict[str, RGB]] = {
    "moonlit": {
        "background": (7, 8, 24), "sky": (35, 31, 66), "star": (218, 224, 245),
        "moon": (242, 224, 174), "cloud": (73, 68, 100), "house": (53, 45, 60),
        "trim": (119, 105, 120), "window": (236, 169, 70), "ground": (24, 31, 32),
        "accent": (188, 94, 57), "specter": (151, 221, 190),
    },
    "harvest": {
        "background": (17, 8, 13), "sky": (63, 24, 37), "star": (255, 215, 155),
        "moon": (255, 175, 73), "cloud": (99, 55, 62), "house": (66, 39, 42),
        "trim": (151, 91, 70), "window": (255, 190, 63), "ground": (38, 31, 20),
        "accent": (236, 93, 35), "specter": (193, 225, 159),
    },
    "spectral": {
        "background": (3, 16, 17), "sky": (17, 55, 56), "star": (187, 247, 221),
        "moon": (168, 246, 209), "cloud": (50, 91, 88), "house": (28, 55, 54),
        "trim": (94, 151, 137), "window": (169, 255, 202), "ground": (14, 35, 29),
        "accent": (81, 218, 160), "specter": (202, 255, 231),
    },
    "monochrome": {
        "background": (7, 7, 8), "sky": (39, 39, 42), "star": (224, 224, 224),
        "moon": (204, 204, 196), "cloud": (92, 92, 96), "house": (59, 59, 62),
        "trim": (137, 137, 141), "window": (215, 215, 200), "ground": (28, 29, 28),
        "accent": (169, 169, 169), "specter": (213, 224, 217),
    },
}

HOUSE = (
    "                         /\\",
    "              /\\        /  \\       /\\",
    "             /  \\______/____\\_____/  \\",
    "            /____\\_____|/\\|_____/____\\",
    "           |  []   |   /____\\   |   []  |",
    "           |       |  /|_[]_|\\  |       |",
    "        /\\_|_______|_|______|_|_|_______|_/\\",
    "       /  \\|  []   | |  []  | |   []  |/  \\",
    "      /____\\_______|_|______|_|_______/____\\",
    "      | [] |  _   _ |  _  _  | _   _  | [] |",
    "      |    | | | | || | || | || | | | |    |",
    "      |____|_|_|_|_||_|_||_|_||_|_|_|_|____|",
    "      |   _    _    |  /\\  |    _    _   |",
    "      |  | |  | |   | /  \\ |   | |  | |  |",
    "      |__|_|__|_|___|/____\\|___|_|__|_|__|",
    "      |              | || |              |",
    "______|______________|_||_|______________|______",
)
HOUSE_WIDTH = max(len(line) for line in HOUSE)
ANNEX = (
    "       /\\       ",
    "      /  \\      ",
    "     /____\\     ",
    "     | [] |     ",
    "     |    |     ",
    "   __|_[]_|__   ",
    "  |  |    |  |  ",
    "  |[]| [] |[]|  ",
    "  |__|____|__|  ",
)
BARE_TREE = (
    "       _/\\_       ",
    "   ___/ /\\ \\___   ",
    "  / _  /  \\  _ \\  ",
    " /_/ \\/ /\\ \\/ \\_\\ ",
    "     / /  \\ \\     ",
    "      / || \\      ",
    "        ||        ",
    "       /||\\       ",
)

CLOUDS = (
    ("      .--.       ", "  .-(    ).     ", " (___.__)__)    "),
    ("   .-~~-.  .--. ", " _(      )(    )", "(______________)"),
    ("    __   _      ", " .(  ).(  ).    ", "(___(__)___)    "),
)
BATS = (("/\\_/\\",), ("\\^v^/",), ("<`~' >",))
FUN_GHOST = (" .-. ", "(o o)", "| O |", "'~~~'")
SCARY_RISER = ("  .-. ", " /x x\\", " |_-_|", " /| |\\", "  / \\")
FUN_WALKERS = ((" o ", "/|\\", "/ \\"), (" /\\ ", "(oo)", " /\\"), (" o ", "<|>", " /\\"))
SCARY_WALKERS = ((" _o ", " /|_", " / >"), (".o. ", "/|\\_", " /\\"), (" o__", "/|  ", " /\\ "))


@dataclass(slots=True)
class Moving:
    x: float
    y: float
    speed: float
    phase: float
    variant: int


@dataclass(slots=True)
class Fixed:
    x: float
    phase: float
    variant: int


class HauntedEstateScene(Scene):
    info = SceneInfo(
        key="haunted_estate",
        name="Haunted Estate",
        description="Moonlit Victorian manor, graveyard, bats, pumpkins, and wandering visitors.",
    )

    def __init__(self, width: int, height: int, config: dict[str, Any], seed: int) -> None:
        width, height = clamp_dimensions(width, height)
        super().__init__(width, height, config, seed)
        self.rng = random.Random(seed)
        self.palette = PALETTES[config["art"]["palette"]]
        elements = config["elements"]
        self.stars = [Fixed(self.rng.random(), self.rng.random() * math.tau, self.rng.randrange(3)) for _ in range(elements["stars"])]
        self.clouds = [Moving(self.rng.random(), 0.05 + self.rng.random() * 0.25, 0.006 + self.rng.random() * 0.009, self.rng.random() * math.tau, self.rng.randrange(len(CLOUDS))) for _ in range(elements["clouds"])]
        self.bats = [Moving(self.rng.random(), 0.12 + self.rng.random() * 0.40, 0.018 + self.rng.random() * 0.025, self.rng.random() * math.tau, self.rng.randrange(len(BATS))) for _ in range(elements["bats"])]
        self.graves = [Fixed(self.rng.random(), self.rng.random() * math.tau, self.rng.randrange(4)) for _ in range(elements["gravestones"])]
        self.apparitions = [Fixed(self.rng.random(), self.rng.random() * math.tau, self.rng.randrange(3)) for _ in range(elements["apparitions"])]
        self.wanderers = [Moving(self.rng.random(), 0.0, 0.008 + self.rng.random() * 0.012, self.rng.random() * math.tau, self.rng.randrange(3)) for _ in range(elements["wanderers"])]
        self.pumpkins = [Fixed(self.rng.random(), self.rng.random() * math.tau, self.rng.randrange(3)) for _ in range(elements["pumpkins"])]
        self.window_phases = [self.rng.random() * math.tau for _ in range(32)]

    @property
    def background(self) -> RGB:
        return self.palette["background"]

    def resize(self, width: int, height: int) -> None:
        self.width, self.height = clamp_dimensions(width, height)

    def update(self, delta: float) -> None:
        super().update(delta)
        for moving in (*self.clouds, *self.bats, *self.wanderers):
            moving.x = (moving.x + moving.speed * max(0.0, min(delta, 0.25)) * float(self.config["elements"]["animationSpeed"])) % 1.15

    @property
    def detail_tier(self) -> str:
        if self.width >= 190 and self.height >= 48:
            return "panoramic"
        if self.width >= 135 and self.height >= 38:
            return "cinematic"
        if self.width < 75 or self.height < 25:
            return "compact"
        return "standard"


    def _sky(self, canvas: FrameBuffer, flash: bool) -> None:
        sky_height = max(8, int(self.height * 0.72))
        sky = mix(self.palette["sky"], (170, 174, 190), 0.62) if flash else self.palette["sky"]
        for y in range(sky_height):
            colour = mix(sky, self.background, y / max(1, sky_height) * 0.78)
            glyph = "·" if y % 3 == 0 else " "
            if glyph != " ":
                for x in range((y * 7) % 11, self.width, 19):
                    canvas.put(x, y, glyph, colour)

    def _stars(self, canvas: FrameBuffer) -> None:
        glyphs = ("·", ".", "*")
        for star in self.stars:
            x = int(star.x * (self.width - 1))
            y = 1 + int(((star.phase / math.tau) * 0.31 % 0.31) * self.height)
            pulse = (math.sin(self.elapsed * 1.7 + star.phase) + 1.0) / 2.0
            glyph = glyphs[2] if pulse > 0.86 else glyphs[star.variant % 2]
            canvas.put(x, y, glyph, mix(self.palette["sky"], self.palette["star"], 0.35 + pulse * 0.65))

    def _moon(self, canvas: FrameBuffer) -> None:
        radius_cap = 5 if self.detail_tier == "compact" else 7 if self.detail_tier == "standard" else 10
        radius_y = max(3, min(radius_cap, self.height // 8))
        radius_x = radius_y * 2
        center_x = int(self.width * (0.76 if self.detail_tier == "panoramic" else 0.72))
        center_y = max(radius_y + 1, int(self.height * 0.19))
        crater_modulus = 19 if self.detail_tier in {"cinematic", "panoramic"} else 29
        for dy in range(-radius_y, radius_y + 1):
            extent = int(radius_x * math.sqrt(max(0.0, 1.0 - (dy / radius_y) ** 2)))
            for dx in range(-extent, extent + 1):
                crater = ((dx * 17 + dy * 31 + self.seed) % crater_modulus) in {2, 3}
                colour = mix(self.palette["moon"], self.palette["sky"], 0.22 if crater else 0.0)
                canvas.put(center_x + dx, center_y + dy, "░" if crater else "█", colour)

    def _clouds(self, canvas: FrameBuffer) -> None:
        for cloud in self.clouds:
            sprite = CLOUDS[cloud.variant]
            x = int(cloud.x * (self.width + 24)) - 24
            y = int(cloud.y * self.height + math.sin(self.elapsed * 0.35 + cloud.phase))
            colour = mix(self.palette["cloud"], self.palette["star"], 0.10)
            canvas.sprite(x, y, sprite, colour)

    def _bats(self, canvas: FrameBuffer) -> None:
        for bat in self.bats:
            flap = int((self.elapsed * 7 + bat.phase) % len(BATS))
            sprite = BATS[(bat.variant + flap) % len(BATS)]
            x = int(bat.x * (self.width + 8)) - 8
            y = int(bat.y * self.height + math.sin(self.elapsed * 1.8 + bat.phase) * 1.8)
            canvas.sprite(x, y, sprite, self.palette["trim"])

    def _distant_forest(self, canvas: FrameBuffer, ground_y: int) -> None:
        if self.detail_tier not in {"cinematic", "panoramic"}:
            return
        tree_colour = mix(self.palette["house"], self.background, 0.54)
        haze_colour = mix(self.palette["cloud"], self.background, 0.72)
        max_height = 7 if self.detail_tier == "cinematic" else 11
        for x in range(2, self.width, 5):
            height = 3 + ((x * 17 + self.seed * 11) % max_height)
            for offset in range(height):
                y = ground_y - offset
                half_width = max(0, (height - offset) // 5)
                glyph = "⠿" if offset < height // 3 else "⠇"
                colour = tree_colour if offset < height - 2 else haze_colour
                for branch_x in range(x - half_width, x + half_width + 1):
                    canvas.put(branch_x, y, glyph, colour)

    def _diorama_fog(self, canvas: FrameBuffer, ground_y: int, foreground: bool = False) -> None:
        if self.detail_tier not in {"cinematic", "panoramic"}:
            return
        glyphs = ("⠁", "⠂", "⠄", "⡀", "⢀", "⠈")
        bands = 2 if foreground else 3
        base_y = ground_y + 1 if foreground else ground_y - 15
        colour = mix(
            self.palette["cloud"],
            self.background if foreground else self.palette["sky"],
            0.68 if foreground else 0.76,
        )
        for band in range(bands):
            y = base_y + band * (2 if foreground else 4)
            drift = int(self.elapsed * (2.0 + band * 0.55))
            step = 4 if foreground else 3
            for x in range(-8, self.width + 8, step):
                pattern = x * 13 + band * 29 + self.seed + drift
                if pattern % 7 in {0, 1, 2}:
                    canvas.put(x, y + ((pattern // 7) % 2), glyphs[pattern % len(glyphs)], colour)

    def _framing_branches(self, canvas: FrameBuffer, ground_y: int) -> None:
        if self.detail_tier != "panoramic":
            return
        colour = mix(self.palette["ground"], self.palette["trim"], 0.16)
        height = min(17, max(9, self.height // 4))
        for side in (-1, 1):
            trunk_x = 3 if side < 0 else self.width - 4
            for offset in range(height):
                y = ground_y - offset
                canvas.put(trunk_x + (offset // 6) * side, y, "╱" if side < 0 else "╲", colour)
                if offset in {5, 9, 13}:
                    reach = min(8, offset // 2 + 2)
                    for step in range(1, reach):
                        x = trunk_x + (offset // 6) * side - step * side
                        canvas.put(x, y - step // 2, "╲" if side < 0 else "╱", colour)


    def _hline(self, canvas: FrameBuffer, left: int, right: int, y: int, colour: RGB) -> None:
        for x in range(left, right + 1):
            canvas.put(x, y, "─", colour)

    def _box(self, canvas: FrameBuffer, left: int, top: int, right: int, bottom: int, colour: RGB) -> None:
        for y in range(top + 1, bottom):
            for x in range(left + 1, right):
                canvas.put(x, y, " ")
        self._hline(canvas, left + 1, right - 1, top, colour)
        self._hline(canvas, left + 1, right - 1, bottom, colour)
        canvas.put(left, top, "┌", colour)
        canvas.put(right, top, "┐", colour)
        canvas.put(left, bottom, "└", colour)
        canvas.put(right, bottom, "┘", colour)
        for y in range(top + 1, bottom):
            canvas.put(left, y, "│", colour)
            canvas.put(right, y, "│", colour)

    def _roof(self, canvas: FrameBuffer, left: int, right: int, peak_y: int, eave_y: int) -> None:
        trim = self.palette["trim"]
        texture = mix(self.palette["house"], trim, 0.24)
        center = (left + right) // 2
        half_width = max(2, (right - left) // 2)
        depth = max(1, eave_y - peak_y)
        canvas.put(center, peak_y - 1, "╷", trim)
        for y in range(peak_y, eave_y):
            spread = max(1, round(half_width * (y - peak_y + 1) / depth))
            roof_left = center - spread
            roof_right = center + spread
            for x in range(roof_left + 1, roof_right):
                canvas.put(x, y, " ")
                if (x + y + self.seed) % 3 == 0:
                    canvas.put(x, y, "⠿" if y > peak_y + depth // 2 else "⠇", texture)
            canvas.put(roof_left, y, "╱", trim)
            canvas.put(roof_right, y, "╲", trim)
        self._hline(canvas, left, right, eave_y, trim)

    def _window(self, canvas: FrameBuffer, x: int, y: int, index: int) -> tuple[int, int]:
        trim = mix(self.palette["trim"], self.palette["house"], 0.18)
        glow = math.sin(self.elapsed * 0.8 + self.window_phases[index % len(self.window_phases)]) > -0.38
        canvas.text(x, y, "┌─┐", trim)
        canvas.put(x, y + 1, "│", trim)
        canvas.put(x + 1, y + 1, "█" if glow else "░", self.palette["window"] if glow else self.palette["house"])
        canvas.put(x + 2, y + 1, "│", trim)
        canvas.text(x, y + 2, "└─┘", trim)
        return x + 1, y + 1

    def _detailed_manor(self, canvas: FrameBuffer, ground_y: int) -> tuple[int, int]:
        house_width = min(112, max(72, int(self.width * 0.48)))
        house_x = (self.width - house_width) // 2
        right = house_x + house_width - 1
        body_top = ground_y - 18
        trim = self.palette["trim"]

        self._box(canvas, house_x, body_top, right, ground_y, trim)
        self._hline(canvas, house_x, right, ground_y - 12, trim)
        self._hline(canvas, house_x, right, ground_y - 6, trim)

        tower_width = max(17, house_width // 5)
        left_tower = house_x + 5
        right_tower = right - tower_width - 5
        tower_top = ground_y - 23
        for chimney_x in (left_tower + tower_width + 5, right_tower - 8):
            self._box(canvas, chimney_x, tower_top - 5, chimney_x + 4, tower_top, trim)
        self._box(canvas, left_tower, tower_top, left_tower + tower_width, ground_y, trim)
        self._roof(canvas, left_tower - 2, left_tower + tower_width + 2, ground_y - 31, tower_top)
        self._box(canvas, right_tower, tower_top, right_tower + tower_width, ground_y, trim)
        self._roof(canvas, right_tower - 2, right_tower + tower_width + 2, ground_y - 31, tower_top)

        center_width = max(25, house_width // 3)
        center_left = house_x + (house_width - center_width) // 2
        center_right = center_left + center_width
        center_top = ground_y - 26
        self._box(canvas, center_left, center_top, center_right, ground_y, trim)
        self._roof(canvas, center_left - 3, center_right + 3, ground_y - 35, center_top)
        shadow = mix(self.palette["house"], self.palette["trim"], 0.18)
        for pilaster_x in range(house_x + 4, right, 8):
            for y in range(body_top + 2, ground_y):
                if canvas.chars[y][pilaster_x] == " ":
                    canvas.put(pilaster_x, y, "│", shadow)
        for y in range(body_top + 2, ground_y):
            for x in range(house_x + 2, right - 1, 3):
                if canvas.chars[y][x] == " " and (x * 11 + y * 17 + self.seed) % 19 == 0:
                    canvas.put(x, y, "⠂", shadow)

        center_x = (center_left + center_right) // 2
        tall_window_top = center_top + 4
        canvas.text(center_x - 3, tall_window_top, "╭─────╮", trim)
        for y in range(tall_window_top + 1, tall_window_top + 5):
            canvas.put(center_x - 3, y, "│", trim)
            canvas.put(center_x + 3, y, "│", trim)
            canvas.put(center_x, y, "█", self.palette["window"])
        canvas.text(center_x - 3, tall_window_top + 5, "╰─────╯", trim)
        self._hline(canvas, house_x + 1, right - 1, body_top + 2, shadow)
        self._hline(canvas, house_x + 1, right - 1, ground_y - 9, shadow)

        windows: list[tuple[int, int]] = []
        window_xs = (
            house_x + 7,
            house_x + 20,
            center_left + 6,
            center_right - 8,
            right - 22,
            right - 9,
        )
        for row, y in enumerate((ground_y - 17, ground_y - 11, ground_y - 5)):
            for column, x in enumerate(window_xs):
                windows.append(self._window(canvas, x, y, row * len(window_xs) + column))

        center_x = (center_left + center_right) // 2
        porch_left = center_x - 11
        porch_right = center_x + 11
        porch_top = ground_y - 9
        self._roof(canvas, porch_left, porch_right, ground_y - 13, porch_top)
        for column_x in (porch_left + 2, porch_right - 2):
            for y in range(porch_top + 1, ground_y):
                canvas.put(column_x, y, "│", trim)
            canvas.put(column_x, porch_top, "┬", trim)
            canvas.put(column_x, ground_y, "┴", trim)
        canvas.put(center_x - 7, ground_y - 6, "♦", self.palette["window"])
        canvas.put(center_x + 7, ground_y - 6, "♦", self.palette["window"])
        door_left = center_x - 4
        self._box(canvas, door_left, ground_y - 8, door_left + 8, ground_y, trim)
        canvas.put(center_x, ground_y - 4, "◆", self.palette["window"])
        self._hline(canvas, center_left - 5, center_right + 5, ground_y - 12, trim)
        for x in range(center_left - 4, center_right + 5, 4):
            canvas.put(x, ground_y - 13, "♢", trim)

        if self.config["experience"]["mode"] == "fun":
            colours = (self.palette["accent"], self.palette["window"], self.palette["specter"])
            for index, x in enumerate(range(house_x + 4, right - 3, 5)):
                canvas.put(x, body_top + 1, "•", colours[index % len(colours)])
        else:
            for index, (x, y) in enumerate(windows[::5]):
                drop = int((self.elapsed * 1.2 + index * 1.7) % 4)
                for offset in range(drop):
                    canvas.put(x, y + 1 + offset, "│", (133, 20, 30))
        return house_x, house_width

    def _manor_steps(self, canvas: FrameBuffer, ground_y: int, house_x: int, house_width: int) -> None:
        if self.detail_tier not in {"cinematic", "panoramic"}:
            return
        center = house_x + house_width // 2
        colour = mix(self.palette["trim"], self.palette["ground"], 0.3)
        for level in range(1, min(4, self.height - ground_y)):
            half_width = 5 + level * 3
            self._hline(canvas, center - half_width, center + half_width, ground_y + level, colour)

    def _house(self, canvas: FrameBuffer) -> tuple[int, int, int]:
        ground_y = self.height - max(5, self.height // 7)
        if self.detail_tier in {"cinematic", "panoramic"}:
            house_x, house_width = self._detailed_manor(canvas, ground_y)
            return ground_y, house_x, house_width

        house_x = (self.width - HOUSE_WIDTH) // 2
        house_y = ground_y - len(HOUSE) + 1
        if self.detail_tier == "standard":
            annex_y = ground_y - len(ANNEX) + 1
            canvas.sprite(house_x - 11, annex_y, ANNEX, self.palette["house"])
            canvas.sprite(house_x + HOUSE_WIDTH - 5, annex_y, ANNEX, self.palette["house"])
        for row, line in enumerate(HOUSE):
            colour = self.palette["trim"] if any(character in line for character in "/\\_") else self.palette["house"]
            canvas.text(house_x, house_y + row, line, colour)
        return ground_y, house_x, HOUSE_WIDTH

    def _ground(self, canvas: FrameBuffer, ground_y: int) -> None:
        for y in range(ground_y, self.height):
            colour = mix(self.palette["ground"], self.background, (y - ground_y) / max(1, self.height - ground_y) * 0.5)
            for x in range(self.width):
                glyph = "─" if y == ground_y else ("⠈" if (x * 13 + y * 7) % 23 == 0 else " ")
                if glyph != " ":
                    canvas.put(x, y, glyph, colour)
        if self.detail_tier in {"cinematic", "panoramic"}:
            fence_y = min(self.height - 2, ground_y + 2)
            fence_colour = mix(self.palette["trim"], self.palette["ground"], 0.42)
            canvas.text(0, fence_y, "─" * self.width, fence_colour)
            for x in range(1, self.width, 6):
                canvas.put(x, fence_y - 1, "♠", fence_colour)
                canvas.put(x, fence_y, "╫", fence_colour)
                if fence_y + 1 < self.height:
                    canvas.put(x, fence_y + 1, "│", fence_colour)

    def _graveyard(self, canvas: FrameBuffer, ground_y: int, house_x: int, house_width: int) -> None:
        for grave in self.graves:
            x = int(grave.x * max(1, self.width - 5))
            if house_x - 2 < x < house_x + house_width + 2 and grave.variant % 2 == 0:
                x = (x + house_width // 2) % max(1, self.width - 5)
            y = ground_y - 2 - grave.variant % 2
            shape = (" _ ", "/ \\", "|_|") if grave.variant % 2 else (".---.", "| + |", "|___|")
            canvas.sprite(x, y - len(shape) + 1, shape, mix(self.palette["trim"], self.palette["ground"], 0.35))

    def _pumpkins(self, canvas: FrameBuffer, ground_y: int) -> None:
        faces = ("(˘)", "(o)", "(^)")
        for pumpkin in self.pumpkins:
            x = int(pumpkin.x * max(1, self.width - 3))
            face = faces[pumpkin.variant] if self.config["experience"]["mode"] == "fun" else ("(▼)", "(x)", "(V)")[pumpkin.variant]
            canvas.text(x, ground_y - 1, face, self.palette["accent"])
            canvas.put(x + 1, ground_y - 2, "'", self.palette["ground"])

    def _figures(self, canvas: FrameBuffer, ground_y: int) -> None:
        fun = self.config["experience"]["mode"] == "fun"
        apparition_sprite = FUN_GHOST if fun else SCARY_RISER
        for apparition in self.apparitions:
            cycle = (self.elapsed * 0.16 + apparition.phase / math.tau) % 1.0
            if cycle > 0.62:
                continue
            x = int(apparition.x * max(1, self.width - 7))
            rise = int((1.0 - min(1.0, cycle / 0.22)) * (len(apparition_sprite) - 1)) if cycle < 0.22 else 0
            canvas.sprite(x, ground_y - len(apparition_sprite) + 1 + rise, apparition_sprite, self.palette["specter"])
        walkers = FUN_WALKERS if fun else SCARY_WALKERS
        for walker in self.wanderers:
            sprite = walkers[walker.variant % len(walkers)]
            x = int(walker.x * (self.width + 6)) - 6
            bob = int(math.sin(self.elapsed * 4.0 + walker.phase) > 0.75)
            canvas.sprite(x, ground_y - len(sprite) + 1 - bob, sprite, self.palette["window"] if fun else self.palette["specter"])

    def _status(self, canvas: FrameBuffer) -> None:
        if not self.config["art"]["showStatus"]:
            return
        mode = self.config["experience"]["mode"].upper()
        label = f"HAUNTED ESTATE  ·  {mode}"
        canvas.text(2, self.height - 1, label[: max(0, self.width - 4)], mix(self.palette["trim"], self.palette["star"], 0.4))

    def render(self) -> FrameBuffer:
        canvas = FrameBuffer(self.width, self.height)
        lightning = self.config["elements"]["lightning"]
        period = max(5.0, 20.0 - lightning * 0.13)
        flash = lightning > 0 and 0.04 < (self.elapsed + (self.seed % 13)) % period < 0.12
        ground_y = self.height - max(5, self.height // 7)
        self._sky(canvas, flash)
        self._stars(canvas)
        self._moon(canvas)
        self._clouds(canvas)
        self._distant_forest(canvas, ground_y)
        self._diorama_fog(canvas, ground_y)
        self._bats(canvas)
        ground_y, house_x, house_width = self._house(canvas)
        self._ground(canvas, ground_y)
        self._manor_steps(canvas, ground_y, house_x, house_width)
        self._graveyard(canvas, ground_y, house_x, house_width)
        self._framing_branches(canvas, ground_y)
        self._diorama_fog(canvas, ground_y, foreground=True)
        self._pumpkins(canvas, ground_y)
        self._figures(canvas, ground_y)
        self._status(canvas)
        return canvas
