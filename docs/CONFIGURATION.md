# Configuration Reference

Omarchtober writes normalized JSON atomically to `~/.config/omarchtober/config.json`. The runtime caps input at 256 KiB and falls back to packaged defaults when the file is missing, malformed, oversized, or invalid. Schema version one is migrated to the complete visual collection.

## Experience

| Key | Values | Default | Meaning |
|---|---|---|---|
| `experience.mode` | `fun`, `scary` | `fun` | Content treatment. The bundled collection is family-safe in both modes; Scary deepens ambience and audio. |
| `experience.scene` | `rotation`, `haunted_estate`, `witching_woods`, `pumpkin_hollow`, `midnight_mausoleum` | `rotation` | Fixed scene or full-collection rotation. Unknown keys fall back safely. |
| `experience.enabledScenes` | array of scene keys | all four | Scenes used while rotating. Empty or unknown lists fall back to the full collection. |
| `experience.rotationSeconds` | 15–900 | 90 | Seconds each scene is displayed before crossfading. |

## Art

| Key | Values | Default | Meaning |
|---|---|---|---|
| `art.theme` | `moonlit`, `harvest`, `spectral`, `midnight` | `moonlit` | Color treatment applied as an overlay; bundled plates are never modified. |
| `art.motion` | 0–2 | 0.7 | Multiplier for breathing scale, fog drift, and lightning frequency. `0` freezes motion. |

## Sound

| Key | Values | Default | Meaning |
|---|---|---|---|
| `sound.enabled` | boolean | `false` | Master audio switch. |
| `sound.volume` | 0–100 | 22 | Output amplitude or `mpv` volume. |
| `sound.source` | `procedural`, `media` | `procedural` | Local synthesis or user-selected file. |
| `sound.mediaPath` | absolute local path | empty | MP3, MP4, M4A, OGG, OPUS, FLAC, WAV, or WEBM; 2 GiB maximum. |
| `sound.wind` | boolean | `true` | Filtered procedural night air. |
| `sound.thunder` | boolean | `true` | Sparse rumbles; softened in Fun mode. |
| `sound.creatures` | boolean | `true` | Nocturnal calls; gentler and higher in Fun mode. |

Procedural layer switches have no effect when `source` is `media`. Custom media uses audio only and loops until the screensaver exits. Only one process becomes the audio leader on multi-monitor systems.

## Integration

| Key | Values | Default | Meaning |
|---|---|---|---|
| `integration.idleEnabled` | boolean | `true` | Follow Omarchy's configured screensaver timeout and Keep Awake state. |
| `integration.exitOnPointerMotion` | boolean | `true` | Pointer movement dismisses; clicks, wheel, and keys always dismiss. |

## Example

```json
{
  "schemaVersion": 2,
  "experience": {
    "mode": "fun",
    "scene": "rotation",
    "enabledScenes": ["haunted_estate", "witching_woods", "pumpkin_hollow", "midnight_mausoleum"],
    "rotationSeconds": 90
  },
  "art": { "theme": "moonlit", "motion": 0.7 },
  "sound": {
    "enabled": false,
    "volume": 22,
    "source": "procedural",
    "mediaPath": "",
    "wind": true,
    "thunder": true,
    "creatures": true
  },
  "integration": { "idleEnabled": true, "exitOnPointerMotion": true }
}
```

Inspect the effective configuration with:

```bash
python3 scripts/omarchtober.py --check-config
```
