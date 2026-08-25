# Black-gold visual system

## Visual identity

- Use a near-black background with restrained bronze and gold illumination.
- Center a young, refined Taoist figure as the recurring identity anchor.
- Use Chinese line-art or carved-light contours rather than photorealistic costume drama.
- Reserve the brightest gold for the hands, energy symbol, or one semantic focal point.
- Keep particles slow and sparse; avoid game-VFX clutter.

## Information structure

Present one concept per screen:

1. Large four-to-six-character literary phrase
2. One short plain-language explanation
3. Stable centered figure or symbolic action

This format prioritizes instant comprehension and saves. Keep the narration emotionally continuous so the video does not feel like unrelated cards.

## Ark prompt routing

- Use `远景|`, `近景|`, or `围合|` scene prefixes with the shared `ark_images.py` script.
- Repeat identity anchors in every prompt: young Taoist, refined face, consistent robe, black-gold line art, restrained golden light.
- Describe camera distance, pose, hand action, energy location, background symbol, and negative constraints explicitly.
- Generate stills first and animate only approved frames.

## Typography and branding

- Render final Chinese text locally.
- Use large warm-white text with selective cinnabar-red emphasis when readability benefits.
- Keep explanations smaller but readable at feed scale.
- Use a cinnabar account seal as a brand layer; keep its exact placement consistent within an account.
- Do not bake water-reflection or manuscript-texture rules from `$dao-ink-video` into this style.

## Covers

- Build both 3:4 and 4:3 covers from one approved, unbranded source frame.
- Preserve figure proportions; crop or mirror without stretching.
- Keep the face, hands, or golden focal symbol inside both crop-safe regions.
- Add exact title and seal locally after cropping.
- Inspect each ratio independently at thumbnail size.

## Audio

- Use the voice configured by `$dao-video`; never substitute silently.
- Normalize BGM around the configured target, historically near `-20 LUFS` for the Qingyunguan preset.
- Use a prominent intro, lower constant body, rising outro, and final fade.
- Remove generated environment audio unless explicitly enabled.
