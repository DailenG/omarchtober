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
PANORAMIC_HOUSE = tuple(
    "".join(character * 2 for character in line)
    for line in HOUSE
    for _ in range(2)
)
PANORAMIC_HOUSE_WIDTH = max(len(line) for line in PANORAMIC_HOUSE)
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
        self.window_phases = [self.rng.random() * math.tau for _ in range(14)]

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
    @property
    def architecture_scale(self) -> int:
        return 2 if self.detail_tier == "panoramic" and self.height >= 70 else 1


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

    def _house(self, canvas: FrameBuffer) -> tuple[int, int, int]:
        ground_y = self.height - max(5, self.height // 7)
        scale = self.architecture_scale
        house = PANORAMIC_HOUSE if scale == 2 else HOUSE
        house_width = PANORAMIC_HOUSE_WIDTH if scale == 2 else HOUSE_WIDTH
        house_x = (self.width - house_width) // 2
        house_y = ground_y - len(house) + 1
        if self.detail_tier in {"cinematic", "panoramic"} and scale == 1:
            annex_y = ground_y - len(ANNEX) + 1
            canvas.sprite(house_x - 11, annex_y, ANNEX, self.palette["house"])
            canvas.sprite(house_x + house_width - 5, annex_y, ANNEX, self.palette["house"])
        if self.detail_tier == "panoramic":
            tree_y = ground_y - len(BARE_TREE) + 1
            canvas.sprite(max(1, house_x - 37), tree_y, BARE_TREE, self.palette["ground"])
            canvas.sprite(min(self.width - 17, house_x + house_width + 19), tree_y, BARE_TREE, self.palette["ground"])
        for row, line in enumerate(house):
            colour = self.palette["trim"] if any(char in line for char in "/\\_") else self.palette["house"]
            canvas.text(house_x, house_y + row, line, colour)
        window_points = ((18, 4), (39, 4), (25, 7), (34, 7), (12, 9), (22, 9), (31, 9), (41, 9), (13, 13), (22, 13), (37, 13), (46, 13))
        for index, (wx, wy) in enumerate(window_points):
            glow = math.sin(self.elapsed * 0.8 + self.window_phases[index]) > -0.38
            if glow:
                for block_y in range(scale):
                    for block_x in range(scale):
                        canvas.put(house_x + wx * scale + block_x, house_y + wy * scale + block_y, "■", self.palette["window"])
        if self.config["experience"]["mode"] == "fun":
            colours = (self.palette["accent"], self.palette["window"], self.palette["specter"])
            step = 4 * scale
            for index, x in enumerate(range(house_x + 10 * scale, house_x + house_width - 7 * scale, step)):
                canvas.put(x, house_y + 10 * scale, "•", colours[index % len(colours)])
        else:
            for index, (wx, wy) in enumerate(window_points[::4]):
                drop = int((self.elapsed * 1.2 + index * 1.7) % (4 * scale))
                for offset in range(drop):
                    canvas.put(house_x + wx * scale, house_y + wy * scale + scale + offset, "│", (133, 20, 30))
        return ground_y, house_x, house_width

    def _ground(self, canvas: FrameBuffer, ground_y: int) -> None:
        for y in range(ground_y, self.height):
            colour = mix(self.palette["ground"], self.background, (y - ground_y) / max(1, self.height - ground_y) * 0.5)
            for x in range(self.width):
                glyph = "_" if y == ground_y else ("," if (x * 13 + y * 7) % 23 == 0 else " ")
                if glyph != " ":
                    canvas.put(x, y, glyph, colour)
        if self.detail_tier in {"cinematic", "panoramic"}:
            fence_y = min(self.height - 2, ground_y + 2)
            for x in range(0, self.width, 6):
                canvas.text(x, fence_y, "†─", mix(self.palette["trim"], self.palette["ground"], 0.4))
        if self.detail_tier == "panoramic":
            fog_colour = mix(self.palette["cloud"], self.background, 0.58)
            for band in range(2):
                y = min(self.height - 1, ground_y + 3 + band * 2)
                offset = int(self.elapsed * (3 + band)) % 17
                for x in range(-offset, self.width, 17):
                    canvas.text(x, y, "~~~~~", fog_colour)

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
        self._sky(canvas, flash)
        self._stars(canvas)
        self._moon(canvas)
        self._clouds(canvas)
        self._bats(canvas)
        ground_y, house_x, house_width = self._house(canvas)
        self._ground(canvas, ground_y)
        self._graveyard(canvas, ground_y, house_x, house_width)
        self._pumpkins(canvas, ground_y)
        self._figures(canvas, ground_y)
        self._status(canvas)
        return canvas
