# Omarchtober Roadmap

The renderer and settings contract are scene-first. Each release should add one complete, original scene rather than partially building several.

## Priority order

1. **Haunted Estate** — available in 0.1. Moonlit Victorian exterior, graveyard, pumpkins, bats, emergers, walkers, and four adaptive detail tiers.
2. **Witching Woods** — crooked forest path, cauldron clearing, ravens, owls, lanterns, and a witch silhouette. Broad appeal and a composition distinct from the estate.
3. **Pumpkin Hollow** — harvest village, hay wagons, corn maze, candy trail, and smiling jack-o'-lanterns. Designed as the strongest Fun-mode scene.
4. **Gothic Manor** — close facade view with many windows, webs, moving curtains, portraits, and hidden silhouettes. Scary mode may add original blood and apparition treatments.
5. **Cemetery Gate** — iron gates, rolling fog, mausoleums, ravens, grave risers, and a distant chapel.
6. **Midnight Carnival** — abandoned midway, carousel silhouettes, flickering bulbs, tents, and original masked performers; no references to identifiable film properties.
7. **Harvest Farm** — cornfield, barn, scarecrows, windmill, and distant storm. Fun mode emphasizes a festival; Scary mode emphasizes moving scarecrows.

## Release gates for every scene

- Complete Fun and Scary treatments; Fun contains no blood, exposed remains, zombies, threatening faces, or jump-scare timing.
- Compact, Standard, Cinematic, and Panoramic compositions.
- Deterministic snapshot at a fixed seed and time.
- Exact configured populations and bounded per-frame work.
- No new runtime dependency without explicit review.
- Original artwork, audio synthesis, names, and archetypes.
- Configuration, website, screenshots, and scene-authoring documentation updated in the same change.

## Platform backlog

- Per-scene presets that do not weaken the global Fun-mode safety override.
- Scene rotation with deterministic minimum durations.
- Reduced-motion treatment separate from population and content mode.
- Optional palette import using local files only.
- Renderer-backend research for a future GPU edition. This remains separate unless it can preserve the scene contract without adding dependencies to the terminal plugin.
