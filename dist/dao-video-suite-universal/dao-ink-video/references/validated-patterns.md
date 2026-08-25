# Reusable visual style patterns from the 青虚观 project

## Baseline

- Video canvas: 1920 × 1080 (16:9)
- Separate Douyin feed cover: 1080 × 1440 portrait
- FPS: 30
- Standard six-screen release duration: 690–780 frames / 23–26 seconds
- Confirmed paced cut: 720 frames / 24 seconds
- A 900-frame / 30-second master remains valid only when the approved main-caption copy naturally supports it
- Water horizon used by the latest composition: y = 715
- Primary composition: `CapCutWaterReflection`

## Pacing baseline

- Keep six screens with two central literary phrases per screen; the modern explanation remains visible but silent.
- Use the configured clone voice, emotion `fluent`, and speed near `1.08` for the standard 23–26-second release cut.
- Add about 0.8 seconds of silence between the six returned TTS groups. Together with natural TTS gaps, aim for roughly 0.9–1.0 seconds between spoken groups.
- Keep about 0.6 seconds before speech and 2.0–2.4 seconds after the final phrase. Do not add narration or rewrite the approved opening merely to increase duration.
- Derive group starts, ends, and second-phrase reveals from the current synthesis timestamps. Fixed frame numbers from one episode are not reusable timing constants.

## Proven visual layer structure

1. Dark olive base
2. Manuscript image tiled horizontally
3. Static sparse gray glyph anchors, visually absorbed into the vertical manuscript system
4. Moving near-black vertical calligraphy layer
5. Mirrored source below the horizon
6. Water-only turbulence and displacement
7. Multiplicative olive grading and center/edge vignettes
8. Translucent vermilion `静心` title and its independent reflection
9. High-contrast foreground captions and smaller explanations
10. Narration audio

This is the series style system, not a requirement to reproduce a reference shot by shot. Vary manuscript content, symbols, title placement, layer density, and motion emphasis according to each original script.

For the established `qingxuguan-ink` account preset, the already approved background typography is an identity exception to that general variation rule: keep the static gray `将 / 进 / 酒 / 莫 / 停` anchors and the moving near-black `君不见黄河 / 人生得意 / 天生我材 / 与尔同销` layer unchanged. Render every background calligraphy item with `writingMode: vertical-rl`. The gray anchors belong to the vertical manuscript texture and must never become a legible horizontal banner. Do not replace them with episode-theme phrases without explicit user approval.

The historical source component placed manuscript, gray glyphs, and black glyphs inside an outer `brightness(0.08) contrast(0.84) saturate(0.68) sepia(0.12) blur(0.5px)` grade. Preserve that grade or an equivalent final luminance. Raw glyph opacity values are not valid review targets; review the final representative frame, where the gray layer should be barely visible.

## Motion formulas

For a seamless 30-second forward-and-back movement:

```ts
const travel = (1 - Math.cos((frame / duration) * Math.PI * 2)) / 2;
const x = startX + travel * distance;
```

Use smaller distance for distant layers and larger distance for near layers. A later accepted experiment kept the sparse gray layer static while retaining movement in the dark layer.

For water evolution visible in a six-second comparison:

```ts
const phase = frame / 150 * Math.PI * 4;
const noiseShift = (frame * 0.9) % 320;
```

The project used fractal noise near `0.0032 0.035` and displacement around `24 ± 7`. These are starting points, not universal targets.

## Reflection geometry

- Mirror the full source layer, not a separately reconstructed approximation.
- Clip reflection below the horizon.
- Use the horizon as the visual joint and tune translation and `scaleY` together.
- The manuscript reflection used approximately `scaleY(-0.72)`.
- The red title used its own reflection geometry around y = 620 and approximately `scaleY(-0.78)`.
- Distort title reflection independently so it never produces a sweep artifact across the main title.
- Attachment is structural: set the mirror line at the source title's visual baseline. Do not move the mirror line below the explanation merely to avoid overlap.
- Layer order: rear title → its reflection → foreground Wei-bei title → explanation. This reproduces the video system while keeping foreground text sharp.
- Only the rear brush title is reflected in the accepted cover system. Do not reflect the foreground Wei-bei title.
- When a cover thumbnail makes the video-strength reflection too faint, increase reflection opacity without changing mirror geometry or water distortion. The accepted cover test increased it from about `0.22` to about `0.42`.

## Feed-cover system

Use a dedicated `1080 × 1440` still composition for the current Douyin feed-cover workflow. Keep core copy centered so it survives portrait grid display and adjacent UI cropping.

Layer order:

1. Near-black base and vignette
2. Full-manuscript image, grayscale and darkened until glyphs are barely visible
3. Large rear brush title in dark vermilion, 100% opacity
4. Rear-title water reflection attached at the title baseline
5. Smaller foreground Wei-bei title, 100% opacity, using warm white plus brighter vermilion
6. Compact Song-style explanation close below the foreground title
7. Small irregular stone-seal brand mark in the upper-right safe area
8. Subtle paper grain

Validated cover decisions:

- Push the rear brush title backward by using a darker color such as deep vermilion, not by lowering opacity.
- Keep both source title layers sharp. Do not use glow, drop shadow, or blur to create hierarchy.
- Apply turbulence/displacement only to the mirrored copy. If red smears appear behind the source title, the reflection layer or clip line is misplaced.
- Keep the explanation close enough to read as part of the title group; do not isolate it far below.
- Treat the brand mark as a handmade seal: asymmetrical contour, muted pigment, slight edge variation. Avoid capsules, gradients, and UI-button styling.
- Judge the result in a three-column feed-grid mockup or at thumbnail scale, not only as a full-size still.

Current reusable implementation in the 青虚观 project:

- Composition: `EpisodeCover`
- Source: `ink-wisdom-video/src/EpisodeCover.tsx`
- Latest validated experiment at the time of this note: `青虚观-得失-封面-v9-石印Logo.png`, with later reflection-strength adjustments retained in source.

## Typography

- Main caption: bold Wei-bei-style font, about 132 px
- Explanation: heavier Song-style font, about 46–48 px
- Title: broad display calligraphy, about 340 px with low opacity
- Caption colors: warm off-white plus selective bright vermilion highlights
- Bundle fonts locally and call `loadFont()` before use

Fonts used in the reference project:

- `WeibeiSC-Bold.otf`
- `FZCuJinLJW.ttf`
- `HeiZhaoBangShu.ttf`
- `MaShanZheng-Regular.ttf`

Do not redistribute these fonts into another project without checking their licenses.

## Iteration lessons

- Render stills first for composition alignment.
- Six-second samples were sufficient for title, water, and parallax comparison.
- Descriptive filenames preserved design intent better than numeric versions alone.
- The iteration path moved from stronger water visibility and vignette, through title-reflection alignment, then typography, complete narration, three-layer parallax, and finally quieter background layers.
- The latest short preview was `v31-深灰黑静止层`; the latest known complete narrated render before it was `v27-三层背景-完整字幕原声版`.
- Do not claim v31 is the approved final merely because it is newest; it was a six-second test.

## Quality checklist

- Title reflection is attached to the waterline and does not cross the source title.
- Main captions remain readable over all background states.
- Spoken narration contains only the visible main-caption phrases, in the same order and with exact wording. Bottom explanations and hidden expansion clauses remain silent.
- Pre-TTS narration validation and post-TTS subtitle-payload validation both pass before rendering.
- Highlighted characters match intended semantics.
- No subtitle gap or overlap is caused by frame conversion.
- Background motion is visible without competing with narration.
- First and last loop frames are visually compatible.
- Full render contains audio and matches composition duration.
- Cover rear title is sharp and 100% opaque; depth comes from darker color.
- Cover reflection touches the rear title at its mirror line and remains behind foreground text.
- Explanation stays close to the title group at feed-thumbnail size.
- Background manuscript is barely visible and does not become readable competing copy.
- Brand mark reads as a seal rather than a pill-shaped badge.
