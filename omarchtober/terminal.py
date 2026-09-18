"""Terminal lifecycle and screensaver dismissal handling."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import termios
import time
import tty
from typing import Any

from .config import clamp_dimensions
from .rendering import RGB


class DismissalInput:
    """Classify SGR mouse reports without swallowing keyboard input."""

    _MOUSE_PREFIX = b"\x1b[<"

    def __init__(self, exit_on_pointer_motion: bool, pending_timeout: float = 0.06) -> None:
        self.exit_on_pointer_motion = exit_on_pointer_motion
        self.pending_timeout = pending_timeout
        self.buffer = bytearray()
        self.pending_since: float | None = None

    def feed(self, data: bytes, now: float | None = None) -> bool:
        timestamp = time.monotonic() if now is None else now
        if data:
            if not self.buffer:
                self.pending_since = timestamp
            self.buffer.extend(data)
        while self.buffer:
            probe = bytes(self.buffer)
            if len(probe) < len(self._MOUSE_PREFIX):
                return not self._MOUSE_PREFIX.startswith(probe)
            if not probe.startswith(self._MOUSE_PREFIX):
                return True
            terminator = -1
            for index, byte in enumerate(self.buffer[3:], start=3):
                if byte in (ord("M"), ord("m")):
                    terminator = index
                    break
                if byte not in b"0123456789;":
                    return True
            if terminator < 0:
                return len(self.buffer) > 32
            fields = bytes(self.buffer[3:terminator]).split(b";")
            if len(fields) != 3 or not all(field.isdigit() for field in fields):
                return True
            button_code = int(fields[0])
            del self.buffer[: terminator + 1]
            if not button_code & 32 or self.exit_on_pointer_motion:
                return True
        self.pending_since = None
        return False

    def expired(self, now: float | None = None) -> bool:
        if not self.buffer or self.pending_since is None:
            return False
        timestamp = time.monotonic() if now is None else now
        return timestamp - self.pending_since >= self.pending_timeout


class TerminalSession:
    def __init__(self, background: RGB) -> None:
        self.background = background
        self.original_attributes: list[Any] | None = None
        self.active = False

    def __enter__(self) -> "TerminalSession":
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise RuntimeError("interactive mode requires a terminal")
        self.original_attributes = termios.tcgetattr(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        red, green, blue = self.background
        sys.stdout.write(
            "\x1b[?1049h\x1b[2J\x1b[H\x1b[?25l"
            "\x1b[?1003h\x1b[?1006h"
            f"\x1b]11;rgb:{red:02x}/{green:02x}/{blue:02x}\x07"
        )
        sys.stdout.flush()
        self.active = True
        return self

    def __exit__(self, *_: Any) -> None:
        if not self.active:
            return
        sys.stdout.write("\x1b[?1003l\x1b[?1006l\x1b[0m\x1b[?25h\x1b[?1049l")
        sys.stdout.flush()
        if self.original_attributes:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.original_attributes)
        self.active = False


def terminal_size() -> tuple[int, int]:
    size = shutil.get_terminal_size(fallback=(120, 36))
    return clamp_dimensions(size.columns, size.lines)


def dismiss_screensaver_windows() -> None:
    try:
        subprocess.Popen(
            ["pkill", "-f", "[o]rg.omarchy.screensaver"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        pass
