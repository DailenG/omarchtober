# Configuration Reference

Omarchtober writes normalized JSON atomically to `~/.config/omarchtober/config.json`. The renderer caps input at 256 KiB and falls back to packaged defaults when the file is missing, malformed, oversized, or invalid.

## Experience

| Key | Values | Default | Meaning |
|---|---|---|---|
| `experience.mode` | `fun`, `scary` | `fun` | Global content treatment. Fun is the family-friendly safety boundary. |
| `experience.scene` | registered scene key | `haunted_estate` | Active scene. Unknown and planned keys fall back safely. |

## Elements

| Key | Range | Default |
|---|---:|---:|
| `stars` | 0–160 | 60 |
| `clouds` | 0–12 | 4 |
| `bats` | 0–40 | 12 |
| `gravestones` | 0–36 | 14 |
| `apparitions` | 0–12 | 4 |
| `wanderers` | 0–10 | 3 |
| `pumpkins` | 0–24 | 8 |
| `lightning` | 0–100 | 25 |
| `animationSpeed` | 0.25–2.0 | 1.0 |

Counts are exact. Adaptive detail tiers never add configured entities. The active scene maps `apparitions` and `wanderers` to mode-safe visual treatments.

## Art

| Key | Values | Default |
|---|---|---|
| `art.palette` | `moonlit`, `harvest`, `spectral`, `monochrome` | `moonlit` |
| `art.showStatus` | boolean | `false` |

Status text is disabled by default so the nightscape remains a pure composition.

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

Procedural layer switches have no effect when `source` is `media`. Custom media uses audio only and loops until the screensaver exits.

## Integration

| Key | Values | Default | Meaning |
|---|---|---|---|
| `integration.idleEnabled` | boolean | `true` | Follow Omarchy's configured screensaver timeout and Keep Awake state. |
| `integration.exitOnPointerMotion` | boolean | `true` | Pointer movement dismisses; clicks and keys always dismiss. |

## Example

```json
{
  "schemaVersion": 1,
  "experience": { "mode": "fun", "scene": "haunted_estate" },
  "elements": {
    "stars": 60,
    "clouds": 4,
    "bats": 12,
    "gravestones": 14,
    "apparitions": 4,
    "wanderers": 3,
    "pumpkins": 8,
    "lightning": 25,
    "animationSpeed": 1.0
  },
  "art": { "palette": "moonlit", "showStatus": false },
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
