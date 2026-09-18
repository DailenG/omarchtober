# Scene Authoring

A scene is an original, deterministic terminal composition registered behind the shared Omarchy lifecycle. It must not implement its own tray, settings store, terminal launch, idle monitor, dismissal decoder, or audio process.

## Files to change

1. Add `omarchtober/scenes/<scene_key>.py` with one `Scene` subclass.
2. Register it in `omarchtober/scenes/__init__.py`.
3. Add public metadata to `scenes.json` and mark it `available`.
4. Add the scene to the available-scene model in `Config.qml`.
5. Add behavioral tests in `tests/`.
6. Update `README.md`, `ROADMAP.md`, configuration documentation, and website gallery.

Do not add a second configuration loader, frame buffer, render loop, audio engine, or scene registry.

## Required contract

```python
from omarchtober.rendering import FrameBuffer, RGB, SceneInfo
from omarchtober.scenes.base import Scene

class NewScene(Scene):
    info = SceneInfo(
        key="new_scene",
        name="New Scene",
        description="One sentence shown in settings.",
    )

    @property
    def background(self) -> RGB:
        return (0, 0, 0)

    def render(self) -> FrameBuffer:
        canvas = FrameBuffer(self.width, self.height)
        # Draw only from initialized state, self.elapsed, and normalized config.
        return canvas
```

Construction must be deterministic for `(width, height, config, seed)`. `update(delta)` must use bounded monotonic deltas. `resize` must not perform unbounded work. Every glyph must occupy one terminal cell.

## Content modes

Fun mode is a safety boundary. It must exclude:

- blood, gore, exposed remains, and corpse detail;
- zombies, threatening skeletons, or menacing apparitions;
- threatening faces, weapons, pursuit, and jump-scare timing;
- audio intended to startle or distress children.

Safe replacements include costumed visitors, smiling pumpkins, friendly ghosts, black cats, candy, colored lights, owls, and gentle weather. A global mode toggle must be sufficient; users must not hunt through per-element controls to remove unsafe content.

Scary mode may use restrained terminal imagery but must remain original. Do not copy or closely evoke identifiable film characters, masks, houses, logos, dialogue, scores, or branded names.

## Adaptive detail

Support all tiers through composition, not glyph scaling:

- Compact: below 75×25.
- Standard: 75×25 and above.
- Cinematic: 135×38 and above.
- Panoramic: 190×48 and above; tall terminals may enlarge focal architecture while adding wide scenery.

Higher tiers may add static scenery, architectural texture, fog layers, and staging. Never change configured entity counts by tier.

## Tests that earn their place

Keep tests for consumer-visible contracts:

- a fixed seed and time produce the same snapshot;
- Fun output excludes the scene's unsafe sprites and includes its safe replacements;
- configured counts are exact;
- each adaptive tier adds its documented composition;
- resize and extreme valid values remain bounded;
- malformed configuration falls back safely.

Do not assert source text, registry wiring, field copies, or implementation-only coordinates.

## Copy-ready AI agent prompt

Replace bracketed values, then give this prompt to an AI coding agent from the repository root:

```text
Add an original Omarchtober scene named [DISPLAY NAME] with key [snake_case_key].

Concept: [two or three sentences describing location, composition, and motion].
Fun treatment: [safe characters, props, and audio mood].
Scary treatment: [optional restrained scary replacements].
Configurable elements: [which existing count controls the scene uses; propose a schema change only if no existing concept fits].

Follow AGENTS.md and docs/SCENE_AUTHORING.md. Reuse Scene, FrameBuffer, configuration normalization, terminal lifecycle, dismissal, and AudioEngine; do not create parallel infrastructure. Implement Compact, Standard, Cinematic, and Panoramic compositions while keeping configured populations exact. Use only original archetypes and single-cell terminal glyphs. Register the scene, expose it in Config.qml, update scenes.json and user documentation, and add only behavioral tests for deterministic output, Fun-mode safety, exact populations, and adaptive detail. Run the documented repository verification commands and include a deterministic snapshot in the result.
```

If an agent proposes a new dependency, asset license, configuration field, or runtime network access, stop and require maintainer review before implementation.
