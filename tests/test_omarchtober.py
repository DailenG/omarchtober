from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from omarchtober.audio import AudioEngine
from omarchtober.config import SCENES, defaults, load_config, normalize_config, validate_media_path

PLAYER_SPEC = spec_from_file_location("visual_player", ROOT / "scripts" / "visual-player.py")
assert PLAYER_SPEC and PLAYER_SPEC.loader
visual_player = module_from_spec(PLAYER_SPEC)
PLAYER_SPEC.loader.exec_module(visual_player)


class ConfigurationTests(unittest.TestCase):
    def test_visual_configuration_is_clamped_and_unknown_values_are_safe(self) -> None:
        config = normalize_config(
            {
                "schemaVersion": 2,
                "experience": {
                    "mode": "nightmare",
                    "scene": "untrusted",
                    "enabledScenes": ["witching_woods", "unknown", "witching_woods"],
                    "rotationSeconds": 9999,
                },
                "art": {
                    "theme": "missing",
                    "motion": -8,
                    "parallax": 8,
                    "effects": {"mist": 8, "flight": -2, "lanterns": "bad", "lightning": 0.4},
                },
                "sound": {"volume": -20, "source": "network", "mediaPath": 5},
                "integration": {"idleEnabled": "yes", "exitOnPointerMotion": False},
            }
        )
        self.assertEqual(config["experience"]["mode"], "fun")
        self.assertEqual(config["experience"]["scene"], "rotation")
        self.assertEqual(config["experience"]["enabledScenes"], ["witching_woods"])
        self.assertEqual(config["experience"]["rotationSeconds"], 900)
        self.assertEqual(
            config["art"],
            {
                "theme": "moonlit",
                "motion": 0,
                "parallax": 2,
                "effects": {"mist": 2, "flight": 0, "lanterns": 0.65, "lightning": 0.4},
            },
        )
        self.assertEqual(config["sound"]["source"], "procedural")
        self.assertEqual(config["sound"]["volume"], 0)
        self.assertEqual(config["sound"]["mediaPath"], "")
        self.assertTrue(config["integration"]["idleEnabled"])
        self.assertFalse(config["integration"]["exitOnPointerMotion"])

    def test_version_one_configuration_migrates_to_full_collection(self) -> None:
        migrated = normalize_config(
            {
                "schemaVersion": 1,
                "experience": {"mode": "scary", "scene": "haunted_estate"},
                "art": {"palette": "harvest"},
            }
        )
        self.assertEqual(migrated["schemaVersion"], 4)
        self.assertEqual(migrated["experience"]["mode"], "scary")
        self.assertEqual(migrated["experience"]["scene"], "rotation")
        self.assertEqual(migrated["experience"]["enabledScenes"], list(SCENES))
        self.assertEqual(migrated["art"]["theme"], "moonlit")

    def test_oversized_or_malformed_file_uses_packaged_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text("{" + "x" * (256 * 1024), encoding="utf-8")
            self.assertEqual(load_config(path), defaults())
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(load_config(path), defaults())


class VisualCollectionTests(unittest.TestCase):
    def test_every_public_scene_has_a_bundled_visual_asset(self) -> None:
        config = defaults()
        paths = visual_player.scene_paths(config)
        self.assertEqual(len(paths), len(SCENES))
        self.assertEqual({path.stem.replace("-", "_") for path in paths}, set(SCENES))
        for path in paths:
            self.assertTrue(path.is_file())
            self.assertGreater(path.stat().st_size, 100_000)

    def test_single_scene_selection_does_not_rotate(self) -> None:
        config = defaults()
        config["experience"]["scene"] = "pumpkin_hollow"
        paths = visual_player.scene_paths(config)
        self.assertEqual([path.name for path in paths], ["pumpkin-hollow.webp"])

    def test_estate_parallax_layer_is_bundled_and_bounded(self) -> None:
        config = defaults()
        config["experience"]["scene"] = "haunted_estate"
        layers = visual_player.scene_layers(visual_player.scene_paths(config))
        self.assertEqual(len(layers), 1)
        self.assertEqual(len(layers[0]), 1)
        layer = layers[0][0]
        self.assertEqual(layer["depth"], 1.0)
        self.assertEqual(layer["xAmplitude"], 18.0)
        self.assertEqual(layer["yAmplitude"], 7.0)
        self.assertEqual(layer["opacity"], 0.5)
        self.assertGreater(Path(layer["source"]).stat().st_size, 100_000)

    def test_session_handoff_exposes_private_normalized_payload(self) -> None:
        config = normalize_config(
            {
                "schemaVersion": 2,
                "experience": {"scene": "witching_woods", "rotationSeconds": 4000},
                "art": {
                    "theme": "spectral",
                    "motion": 9,
                    "parallax": 0.8,
                    "effects": {"mist": 0.2, "flight": 0.4, "lanterns": 0.6, "lightning": 0.8},
                },
                "integration": {"exitOnPointerMotion": False},
            }
        )
        paths = visual_player.scene_paths(config)
        with tempfile.TemporaryDirectory() as directory:
            previous = os.environ.get("XDG_RUNTIME_DIR")
            os.environ["XDG_RUNTIME_DIR"] = directory
            try:
                session = visual_player.write_session(config, paths)
            finally:
                if previous is None:
                    del os.environ["XDG_RUNTIME_DIR"]
                else:
                    os.environ["XDG_RUNTIME_DIR"] = previous
            payload = json.loads(session.read_text(encoding="utf-8"))
            self.assertEqual(session.stat().st_mode & 0o777, 0o600)
            self.assertEqual(list(session.parent.glob("*")), [session])
        self.assertEqual(payload["scenes"], [str(paths[0])])
        self.assertEqual(payload["duration"], 900)
        self.assertEqual(payload["theme"], "spectral")
        self.assertEqual(payload["motion"], 2.0)
        self.assertEqual(payload["parallaxDepth"], 0.8)
        self.assertEqual(len(payload["layers"]), 1)
        self.assertEqual(payload["layers"][0], [])
        self.assertEqual(payload["effects"], {"mist": 0.2, "flight": 0.4, "lanterns": 0.6, "lightning": 0.8})
        self.assertFalse(payload["exitOnMotion"])


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
