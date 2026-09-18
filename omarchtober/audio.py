"""Single-leader procedural ambience and user-selected media playback."""

from __future__ import annotations

import fcntl
import math
import os
import random
import shutil
import struct
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from .config import validate_media_path

SAMPLE_RATE = 24_000


def ensure_private_directory(path: Path) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not path.is_dir() or path.is_symlink():
        raise OSError(f"unsafe runtime directory: {path}")
    path.chmod(0o700)


def open_lock_file(path: Path) -> Any:
    flags = os.O_CREAT | os.O_RDWR | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    file = os.fdopen(descriptor, "r+b", buffering=0)
    if not path.is_file() or path.is_symlink():
        file.close()
        raise OSError(f"unsafe audio lock: {path}")
    os.fchmod(file.fileno(), 0o600)
    return file


def runtime_directory() -> Path:
    configured = os.environ.get("XDG_RUNTIME_DIR", "")
    if configured and Path(configured).is_absolute():
        return Path(configured) / "omarchtober"
    cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return cache / "omarchtober" / "runtime"


class AudioEngine:
    """Own exactly one ambience stream across all monitor renderers."""

    def __init__(self, config: dict[str, Any], diagnostic: bool = False) -> None:
        self.config = config
        self.sound = config["sound"]
        self.diagnostic = diagnostic
        self.volume = max(0.0, min(1.0, self.sound["volume"] / 100.0))
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.process: subprocess.Popen[bytes] | None = None
        self.lock_file: Any = None
        self.last_error = ""
        self.rng = random.Random(os.getpid() ^ time.time_ns())

    @staticmethod
    def playback_command() -> list[str]:
        return [
            "pw-cat", "--playback", "--raw", "--format", "s16",
            "--rate", str(SAMPLE_RATE), "--channels", "2", "-",
        ]

    def _acquire(self) -> bool:
        if self.volume <= 0:
            self.last_error = "volume is zero"
            return False
        try:
            directory = runtime_directory()
            ensure_private_directory(directory)
            self.lock_file = open_lock_file(directory / "audio.lock")
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except BlockingIOError:
            self.last_error = "another Omarchtober process already owns the audio stream"
        except OSError as error:
            self.last_error = f"cannot create the audio lock: {error}"
        if self.lock_file:
            self.lock_file.close()
            self.lock_file = None
        return False

    def start(self) -> bool:
        if not self._acquire():
            return False
        if self.sound["source"] == "media":
            return self._start_media()
        return self._start_procedural()

    def _start_media(self) -> bool:
        path, error = validate_media_path(self.sound["mediaPath"])
        if error:
            self.last_error = error
            self.close()
            return False
        if not shutil.which("mpv"):
            self.last_error = "mpv is unavailable; custom media playback cannot start"
            self.close()
            return False
        assert path is not None
        try:
            self.process = subprocess.Popen(
                [
                    "mpv", "--no-video", "--loop-file=inf", "--really-quiet",
                    f"--volume={round(self.volume * 100)}", "--", str(path),
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        except OSError as error_value:
            self.last_error = f"cannot start mpv: {error_value}"
            self.close()
            return False
        time.sleep(0.1)
        if self.process.poll() is not None:
            self.last_error = self._process_error("mpv exited before playback")
            self.close()
            return False
        return True

    def _start_procedural(self) -> bool:
        if not self.diagnostic and not any(self.sound[key] for key in ("wind", "thunder", "creatures")):
            self.last_error = "all procedural ambience layers are disabled"
            self.close()
            return False
        if not shutil.which("pw-cat"):
            self.last_error = "pw-cat is unavailable; install PipeWire tools"
            self.close()
            return False
        try:
            self.process = subprocess.Popen(
                self.playback_command(),
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        except OSError as error:
            self.last_error = f"cannot start pw-cat: {error}"
            self.close()
            return False
        self.thread = threading.Thread(target=self._synthesise, name="omarchtober-audio", daemon=True)
        self.thread.start()
        time.sleep(0.08)
        if self.process.poll() is not None:
            self.last_error = self._process_error("pw-cat exited before playback")
            self.close()
            return False
        return True

    def _process_error(self, fallback: str) -> str:
        if self.process and self.process.stderr:
            try:
                return self.process.stderr.read().decode("utf-8", errors="replace").strip() or fallback
            except OSError:
                pass
        return fallback

    def _synthesise(self) -> None:
        assert self.process and self.process.stdin
        block_size = 480
        low_noise = 0.0
        wind_phase = 0.0
        thunder_remaining = 0
        thunder_length = 1
        creature_remaining = 0
        creature_length = 1
        creature_phase = 0.0
        rendered = 0
        fun = self.config["experience"]["mode"] == "fun"
        while not self.stop_event.is_set() and self.process.poll() is None:
            block = bytearray(block_size * 4)
            for index in range(block_size):
                wind = 0.0
                if self.sound["wind"]:
                    low_noise = low_noise * 0.992 + self.rng.uniform(-1.0, 1.0) * 0.008
                    wind_phase += math.tau * 0.09 / SAMPLE_RATE
                    wind = low_noise * 1.7 + math.sin(wind_phase) * 0.08
                if self.sound["thunder"] and thunder_remaining <= 0 and self.rng.random() < 0.000008:
                    thunder_length = self.rng.randint(SAMPLE_RATE, SAMPLE_RATE * 3)
                    thunder_remaining = thunder_length
                thunder = 0.0
                if self.sound["thunder"] and thunder_remaining > 0:
                    progress = 1.0 - thunder_remaining / thunder_length
                    envelope = math.sin(math.pi * progress) ** 2 * (1.0 - progress * 0.65)
                    thunder = (math.sin(rendered * math.tau * 43 / SAMPLE_RATE) + self.rng.uniform(-0.5, 0.5)) * envelope * (0.10 if fun else 0.30)
                    thunder_remaining -= 1
                if self.sound["creatures"] and creature_remaining <= 0 and self.rng.random() < 0.000012:
                    creature_length = self.rng.randint(7000, 14_000)
                    creature_remaining = creature_length
                    creature_phase = 0.0
                creature = 0.0
                if self.sound["creatures"] and creature_remaining > 0:
                    progress = 1.0 - creature_remaining / creature_length
                    frequency = (520.0 if fun else 210.0) + math.sin(progress * math.tau * 2) * (35.0 if fun else 18.0)
                    creature_phase += math.tau * frequency / SAMPLE_RATE
                    creature = math.sin(creature_phase) * math.sin(math.pi * progress) ** 2 * 0.12
                    creature_remaining -= 1
                diagnostic = 0.0
                if self.diagnostic and rendered < int(SAMPLE_RATE * 1.8):
                    note = min(2, rendered // int(SAMPLE_RATE * 0.6))
                    within = rendered % int(SAMPLE_RATE * 0.6)
                    progress = within / (SAMPLE_RATE * 0.6)
                    frequency = (440.0, 660.0, 880.0)[note]
                    diagnostic = math.sin(math.tau * frequency * rendered / SAMPLE_RATE) * math.sin(math.pi * progress) ** 2 * 0.42
                sample = int(max(-1.0, min(1.0, wind + thunder + creature + diagnostic)) * self.volume * 32767)
                struct.pack_into("<hh", block, index * 4, sample, sample)
                rendered += 1
            try:
                self.process.stdin.write(block)
                self.process.stdin.flush()
            except (BrokenPipeError, OSError):
                break

    def close(self) -> None:
        self.stop_event.set()
        if self.thread and self.thread.is_alive() and threading.current_thread() is not self.thread:
            self.thread.join(timeout=0.35)
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=0.6)
            except subprocess.TimeoutExpired:
                self.process.kill()
        if self.lock_file:
            try:
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            self.lock_file.close()
            self.lock_file = None
