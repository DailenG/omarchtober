# Scene Authoring

A scene is one original 16:9 illustrated plate presented by the shared visual player. A scene never implements its own window, tray entry, settings store, idle monitor, dismissal handling, or audio process.

## Files to change

1. Add `assets/scenes/<scene-key>.webp` — 2560×1440, compressed WebP, under 5 MiB.
2. For real parallax, add `assets/parallax/<scene-file-stem>/layers.json` and transparent 2560×1440 WebP layer files. Layers must be authored or carefully source-derived; never use automated segmentation.
3. Add the snake-case key to `SCENES` in `omarchtober/config.py`.
4. Map the key to its file in `SCENE_FILES` in `scripts/visual-player.py`.
5. Add public metadata to `scenes.json`.
6. Add the scene to the `scenes` model in `Config.qml`.
7. Add or extend behavioral tests in `tests/`.
8. Update `README.md`, `docs/CONFIGURATION.md`, `docs/index.html`, and the project preview.

Do not add a second configuration loader, player, asset resolver, or catalog.

## Visual contract

Every plate must belong to the same collection at a glance:

- landscape 16:9 with a single dominant focal structure and clear silhouette reading;
- midnight navy sky, near-black ground, ivory moonlight;
- lavender etched contours and restrained warm amber window and lantern light;
- dense stippling, hatch, and Braille-like dithering as the primary texture;
- four depth layers: foreground framing, mid architecture, treeline or horizon, sky;
- no text, logos, watermarks, UI, or signatures;
- composition readable in full-frame `PreserveAspectFit` presentation at 16:9, 16:10, and 21:9.

## Parallax layer contract

Parallax layers use the same `2560×1440` canvas as their base plate and preserve alpha outside the intended foreground. `layers.json` lists local layer files and bounded `depth`, `xAmplitude`, `yAmplitude`, and `opacity` values. At `art.parallax: 0`, the player must hide every supplied layer and reproduce the unmodified base plate. Test the static, default, and maximum depth settings at 4K before release.

## Content safety

Fun mode is the default and must remain genuinely family-friendly. Plates must exclude blood, gore, exposed remains, zombies, threatening faces, weapons, pursuit imagery, and any composition intended to startle. Safe archetypes include manors, chapels, lanterns, pumpkins, cats, owls, ravens, fog, cloaked visitors, mushrooms, and harvest props.

Scary mode may deepen atmosphere and audio. It may not introduce content banned above, because the same bundled plates serve both modes.

Use original architecture and archetypes. Never reproduce identifiable film characters, masks, houses, logos, dialogue, scores, or branded names.

## Acceptance checks

- `python3 scripts/omarchtober.py --list-scenes` includes the key.
- `python3 -m unittest discover -s tests` passes, including the bundled-asset coverage test.
- The plate renders correctly full-screen and during crossfade at motion `0` and `2`.
- The asset is a regular local file committed to the repository; no runtime download exists.
- Configuration, catalog, website, and preview updates ship in the same change.

## Copy-ready AI agent prompt

```text
Add an original Omarchtober scene named [DISPLAY NAME] with key [snake_case_key].

Concept: [two or three sentences describing location, focal structure, and depth layers].
Required style: midnight navy sky, near-black ground, ivory moonlight, lavender etched contours, restrained amber lamp light, dense stippled and Braille-like dithering, four depth layers, no text or logos, 2560x1440 landscape.
Content safety: family-friendly Halloween archetypes only; no blood, gore, remains, zombies, threatening faces, weapons, or pursuit.

Follow AGENTS.md and docs/SCENE_AUTHORING.md. Add assets/scenes/[scene-key].webp, register the key in omarchtober/config.py and scripts/visual-player.py, add catalog entries to scenes.json and Config.qml, update user documentation and the project preview, and add only behavioral tests. Run the documented verification commands and report results.
```

If an agent proposes a new dependency, remote asset, configuration field, or runtime network access, stop and require maintainer review.
