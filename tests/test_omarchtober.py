from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from omarchtober.audio import AudioEngine
from omarchtober.config import defaults, load_config, normalize_config, validate_media_path
from omarchtober.scenes.haunted_estate import HauntedEstateScene
from omarchtober.terminal import DismissalInput


class ConfigurationTests(unittest.TestCase):
    def test_public_configuration_is_clamped_and_unknown_values_are_safe(self) -> None:
        config = normalize_config(
            {
                "experience": {"mode": "nightmare", "scene": "untrusted"},
                "elements": {"stars": 9999, "clouds": -4, "bats": "17", "animationSpeed": 8},
                "art": {"palette": "missing", "showStatus": "yes"},
                "sound": {"volume": -20, "source": "network", "mediaPath": 5},
                "integration": {"idleEnabled": "yes", "exitOnPointerMotion": False},
            }
        )
        self.assertEqual(config["experience"], {"mode": "fun", "scene": "haunted_estate"})
        self.assertEqual(config["elements"]["stars"], 160)
        self.assertEqual(config["elements"]["clouds"], 0)
        self.assertEqual(config["elements"]["bats"], 17)
        self.assertEqual(config["elements"]["animationSpeed"], 2.0)
        self.assertEqual(config["art"], {"palette": "moonlit", "showStatus": False})
        self.assertEqual(config["sound"]["source"], "procedural")
        self.assertEqual(config["sound"]["volume"], 0)
        self.assertEqual(config["sound"]["mediaPath"], "")
        self.assertTrue(config["integration"]["idleEnabled"])
        self.assertFalse(config["integration"]["exitOnPointerMotion"])

    def test_oversized_or_malformed_file_uses_packaged_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text("{" + "x" * (256 * 1024), encoding="utf-8")
            self.assertEqual(load_config(path), defaults())
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(load_config(path), defaults())


class SceneBehaviorTests(unittest.TestCase):
    def config(self, mode: str = "fun") -> dict[str, object]:
        config = defaults()
        config["experience"]["mode"] = mode
        config["elements"].update(
            {"stars": 0, "clouds": 0, "bats": 0, "gravestones": 0, "apparitions": 1, "wanderers": 0, "pumpkins": 0, "lightning": 0}
        )
        return config

    def test_fun_mode_replaces_undead_with_friendly_figures(self) -> None:
        fun = HauntedEstateScene(120, 36, self.config("fun"), seed=4)
        scary = HauntedEstateScene(120, 36, self.config("scary"), seed=4)
        fun.apparitions[0].x = scary.apparitions[0].x = 0.05
        fun.apparitions[0].phase = scary.apparitions[0].phase = 0.0
        fun.elapsed = scary.elapsed = 1.5
        fun_frame = fun.render().plain()
        scary_frame = scary.render().plain()
        self.assertIn("(o o)", fun_frame)
        self.assertNotIn("/x x\\", fun_frame)
        self.assertIn("/x x\\", scary_frame)
        self.assertNotIn("(o o)", scary_frame)

    def test_configured_populations_are_exact(self) -> None:
        config = self.config()
        config["elements"].update({"stars": 17, "clouds": 3, "bats": 9, "gravestones": 11, "apparitions": 5, "wanderers": 4, "pumpkins": 7})
        scene = HauntedEstateScene(120, 36, config, seed=9)
        self.assertEqual(
            [len(scene.stars), len(scene.clouds), len(scene.bats), len(scene.graves), len(scene.apparitions), len(scene.wanderers), len(scene.pumpkins)],
            [17, 3, 9, 11, 5, 4, 7],
        )

    def test_large_displays_gain_detail_without_extra_creatures(self) -> None:
        config = self.config()
        config["elements"]["apparitions"] = 0
        compact = HauntedEstateScene(70, 22, copy.deepcopy(config), seed=2)
        cinematic = HauntedEstateScene(150, 42, copy.deepcopy(config), seed=2)
        panoramic = HauntedEstateScene(200, 52, copy.deepcopy(config), seed=2)
        self.assertEqual((compact.detail_tier, cinematic.detail_tier, panoramic.detail_tier), ("compact", "cinematic", "panoramic"))
        self.assertNotIn("†─", compact.render().plain())
        self.assertIn("†─", cinematic.render().plain())
        self.assertIn("~~~~~", panoramic.render().plain())
        self.assertEqual(len(compact.bats), len(panoramic.bats))

    def test_snapshot_is_deterministic_for_seed_and_time(self) -> None:
        left = HauntedEstateScene(100, 30, self.config(), seed=21)
        right = HauntedEstateScene(100, 30, self.config(), seed=21)
        left.update(3.25)
        right.update(3.25)
        self.assertEqual(left.render().plain(), right.render().plain())


class MediaAndAudioTests(unittest.TestCase):
    def test_media_validation_accepts_local_allowlisted_regular_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ambience.mp3"
            path.write_bytes(b"ID3")
            resolved, error = validate_media_path(str(path))
            self.assertEqual(resolved, path)
            self.assertEqual(error, "")

    def test_media_validation_rejects_symlinks_and_unknown_formats(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "ambience.mp3"
            target.write_bytes(b"ID3")
            link = root / "linked.mp3"
            link.symlink_to(target)
            self.assertIsNone(validate_media_path(str(link))[0])
            unknown = root / "ambience.exe"
            unknown.write_bytes(b"MZ")
            self.assertIsNone(validate_media_path(str(unknown))[0])

    def test_pipewire_stream_declares_raw_stereo_pcm(self) -> None:
        command = AudioEngine.playback_command()
        self.assertEqual(command[0], "pw-cat")
        self.assertIn("--raw", command)
        self.assertEqual(command[command.index("--format") + 1], "s16")
        self.assertEqual(command[command.index("--channels") + 1], "2")


class DismissalInputTests(unittest.TestCase):
    def test_pointer_motion_follows_setting_but_clicks_always_dismiss(self) -> None:
        motion = b"\x1b[<35;15;8M"
        click = b"\x1b[<0;15;8M"
        self.assertTrue(DismissalInput(True).feed(motion, now=1.0))
        self.assertFalse(DismissalInput(False).feed(motion, now=1.0))
        self.assertTrue(DismissalInput(False).feed(click, now=1.0))

    def test_fragmented_mouse_report_waits_for_completion(self) -> None:
        decoder = DismissalInput(False)
        self.assertFalse(decoder.feed(b"\x1b[<35;", now=1.0))
        self.assertFalse(decoder.feed(b"12;8M", now=1.01))
        self.assertFalse(decoder.expired(now=1.02))


class IdleIntegrationTests(unittest.TestCase):
    def run_helper(self, state_home: Path, action: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["XDG_STATE_HOME"] = str(state_home)
        return subprocess.run(
            ["bash", str(ROOT / "scripts" / "idle-integration"), action],
            check=check,
            text=True,
            capture_output=True,
            env=environment,
        )

    def test_owned_toggle_is_released(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            self.run_helper(state, "enable")
            toggle = state / "omarchy" / "toggles" / "screensaver-off"
            owner = state / "omarchtober" / "owns-screensaver-off"
            self.assertEqual(toggle.read_bytes(), owner.read_bytes())
            self.run_helper(state, "disable")
            self.assertFalse(toggle.exists())
            self.assertFalse(owner.exists())

    def test_preexisting_user_toggle_is_never_removed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            toggle = state / "omarchy" / "toggles" / "screensaver-off"
            toggle.parent.mkdir(parents=True)
            toggle.touch()
            self.run_helper(state, "enable")
            self.run_helper(state, "disable")
            self.assertTrue(toggle.exists())

    def test_symlinked_owner_is_refused_without_touching_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            owner = state / "omarchtober" / "owns-screensaver-off"
            owner.parent.mkdir(parents=True)
            target = state / "target"
            target.write_text("preserve me", encoding="utf-8")
            owner.symlink_to(target)
            result = self.run_helper(state, "enable", check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_text(encoding="utf-8"), "preserve me")


if __name__ == "__main__":
    unittest.main()
