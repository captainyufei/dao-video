---
name: dao-ink-video
description: "Create the ink-wash branch of the Dao video series: compare cultural accounts, verify copy sources, write original rhythmic narration, and produce calligraphy, manuscript-parallax, attached water-reflection, Wei-bei caption, stone-seal, and matching feed-cover visuals with Remotion. Use for 青虚观、水墨国风、书法背景、水中倒影、魏碑字幕、水墨封面 or when $dao-video selects the qingxuguan-ink style."
---

# Dao Ink Video

Create the water-reflection and calligraphy branch of the Dao series as an independent project. Read `$dao-video` as the proven operational reference, but do not require a shared repository or move files between projects. Adopt its confirmed state management, approval gates, timestamp, audio, packaging, publishing-handoff, and review practices while keeping the ink implementation and assets local. For fresh competitor research, combine `$account-video-downloader`, `$batch-video-transcribe`, and the relevant platform account-analysis skill before updating this style's references.

## Maturity model

- Treat the black-gold project as the operational reference because it has produced multiple normal videos.
- Treat the ink project as `validation` until it completes multiple repeatable episodes with stable video, audio, captions, covers, packaging, and post-publication records.
- Read [references/mature-workflow-adoption.md](references/mature-workflow-adoption.md) before starting or resuming an ink episode.
- Keep both projects independent. Copy proven rules and small utilities only after verifying them locally; do not create runtime dependencies on another project's private config or assets.

## Workflow

1. Inspect the workspace and research assets.
   - Locate source video, audio, subtitles, fonts, extracted frames, existing compositions, previews, and final renders.
   - Read `package.json`, the Remotion root/composition registration, and the most recently modified implementation.
   - Check Git status without assuming generated files are disposable.
   - Identify the latest accepted full video, cover, and experimental preview separately.
   - Read the local episode manifest and state. If absent, initialize the minimal structure from [references/mature-workflow-adoption.md](references/mature-workflow-adoption.md).

2. Select a topic and title formula.
   - Read [references/yunxuguan-content-formulas.md](references/yunxuguan-content-formulas.md).
   - Start from a current emotional tension that maps to 静心、自持、止语、不争、守时、取舍 or 守拙.
   - Score the topic for pain intensity, instant recognition, title compactness, save/share usefulness, and visual symbolism.
   - Generate compact-action, paradox, and problem-to-outcome title variants before selecting one.

3. Research copy sources and reusable seed material.
   - Search distinctive phrases in quotation marks and search multi-line combinations.
   - Locate the earliest reliably dated appearances available; distinguish ancient primary text, later commentary, modern aphorism, fiction, song, and unattributed repost.
   - Verify alleged classical quotations against primary or authoritative text repositories.
   - Mark uncertain attribution explicitly. Do not label modern internet prose as《道德经》《庄子》《鬼谷子》or a Taoist canon without evidence.
   - Read [references/copy-origin-and-originality.md](references/copy-origin-and-originality.md) for the current project's findings and writing guardrails.

4. Write a new episode with the learned formula.
   - Select one emotional need: calm, restraint, non-contention, letting go, returning to simplicity, or adapting like water.
   - Anchor the script in one verified classical idea or clearly label it as contemporary reflection.
   - Create a fresh thesis, progression, metaphors, sentence structures, and ending.
   - For the established Qingxuguan ink format, make the voiced narration itself a sequence of literary four-to-six-character phrases. Store modern plain-Chinese explanations separately as non-voiced screen text.
   - Enforce “what is seen is what is heard”: after punctuation is removed, every spoken phrase must match one visible main-caption phrase exactly, in the same order. Do not voice explanations, transitions, literary expansion clauses, introductions, or conclusions that are absent from the main caption layer.
   - Before paid TTS, compare `narration.txt` with an explicit main-caption list and stop on any extra, missing, changed, or reordered phrase. After TTS, repeat the comparison against the synthesis subtitle payload before rendering.
   - For the standard six-screen / twelve-phrase ink format, target 23–26 seconds. Keep approved copy and its opening unchanged; never add voiced explanations, transitions, or filler to reach duration.
   - Use the configured ink clone voice with `fluent` at about `1.08` for the standard paced cut. Add about 0.8 seconds of silence between TTS groups, about 0.6 seconds of opening lead-in, and about 2.0–2.4 seconds of closing hold. Recompute all boundaries from the current TTS timestamps instead of copying episode-specific frame numbers.
   - Avoid synonym replacement, line shuffling, or retaining the source's sequence; these are rewrites, not meaningful original creation.
   - Run phrase searches on the finished hook and strongest lines. Rewrite any long distinctive match.

5. Build in independent visual layers.
   - Probe resolution, frame rate, duration, audio presence, and subtitle timing from successful examples.
   - Record the horizon, title position, font character, color hierarchy, background density, reflection geometry, motion direction, and transition timing.
   - Use a base paper/ink image or procedural background.
   - Put distant gray calligraphy, middle manuscript texture, and near black glyphs in separate layers.
   - Render the established `qingxuguan-ink` video body at `1920 × 1080` (16:9). Build the Douyin feed cover separately at `1080 × 1440`; never apply the cover canvas to the video body.
   - Reuse the validated fixed background typography instead of adapting it to each episode: faint static gray anchors `将 / 进 / 酒 / 莫 / 停`, plus the slowly moving near-black groups `君不见黄河 / 人生得意 / 天生我材 / 与尔同销`. Render all background calligraphy with vertical writing direction (`writingMode: vertical-rl`). The gray anchors must not read as a horizontal title banner. Change only foreground episode copy unless the user explicitly requests a new background system.
   - Judge background glyph brightness only after the complete composite grade. The source-layer opacity is not a final visual target: reproduce the historical outer grade `brightness(0.08) contrast(0.84) saturate(0.68) sepia(0.12) blur(0.5px)` or a visually equivalent result. If the large gray glyphs are immediately readable, the background fails review.
   - Complete one forward-and-back background movement over the actual composition duration with `travel = (1 - Math.cos((frame / duration) * Math.PI * 2)) / 2`; the turn occurs at the midpoint. Keep the gray layer static.
   - Animate each layer independently when parallax is required; keep intentionally static layers static.
   - Create water reflection by mirroring the source around an explicit horizon and clipping it below that line.
   - Apply turbulence/displacement only inside the reflected region unless the reference visibly distorts the source layer.
   - Render title, title reflection, foreground captions, explanations, audio, vignette, and grading as separate concerns.

6. Build a separate feed-cover composition.
   - Read [references/validated-patterns.md](references/validated-patterns.md), including the cover system and reflection rules.
   - Do not rely on an arbitrary first frame. Register a dedicated cover composition in the same Remotion project.
   - Design for the platform's portrait feed crop and keep the title, explanation, and brand mark inside the central safe area.
   - Use a dark manuscript texture, a sharp 100%-opaque dark-vermilion brush title behind, and a smaller 100%-opaque Wei-bei title in warm white plus bright vermilion in front.
   - Create the cover reflection from the same large brush-title source and the same mirror geometry used by the video. Attach it at the source baseline; place foreground Wei-bei text and explanation above the reflection layer.
   - Use color value, not opacity, to push the large rear title backward. Never add glow or drop shadow unless the reference visibly contains it.
   - Keep the explanation close to the foreground title. Darken manuscript glyphs until they read as texture rather than competing copy.
   - Use an irregular, muted-vermilion stone-seal brand mark rather than a modern pill-shaped badge.

7. Align captions to audio.
   - Prefer supplied SRT timings; otherwise derive timing from waveform or speech boundaries.
   - Store timings in frame numbers using the composition FPS.
   - Represent each caption group with `from`, `to`, phrases, reveal frames, highlighted character indices, and explanation text.
   - Verify Chinese characters against source text. Do not silently normalize uncertain wording.

8. Iterate with short previews.
   - Render one representative still before video.
   - Render a 5–6 second sample that includes visible background motion, reflection distortion, title, and at least one caption transition.
   - Change one visual dimension per version and name the output after that change.
   - Compare composition, legibility, motion strength, and reflection attachment before rendering the full duration.
   - Preview the cover at full resolution and at approximate feed-thumbnail size; defects hidden at full size may dominate in the feed grid.

9. Render and validate.
   - Run lint and TypeScript checks.
   - Confirm all registered compositions load and local fonts/assets resolve.
   - Probe output duration, dimensions, frame rate, and audio stream.
   - Inspect the first frame, a caption transition, a mid-video frame, and the ending.
   - Keep the best short preview and latest full render clearly identified in the handoff.
   - Export the accepted cover as a clearly named still and verify its dimensions and crop safety.
   - Package only the accepted video, confirmed covers, approved title/caption/topics, and manifest into the release directory.
   - Record whether the episode is still an experiment, ready to upload, awaiting publication confirmation, or published.

## Implementation rules

- Use deterministic frame-based animation through `useCurrentFrame`, `interpolate`, or periodic functions.
- Use explicit constants for FPS, duration, horizon, travel distance, reflection scale, and font families.
- Base seamless ping-pong motion on a periodic cosine curve; ensure the loop's first and last visual states join naturally.
- Load bundled Chinese fonts explicitly and retain system fallbacks.
- Keep SVG filter IDs unique across compositions.
- Keep title source, title reflection, foreground title, explanation, and brand mark as independent layers; never fake a reflection with a blurred duplicate behind the title.
- For attached reflections, set the mirror line at the reflected source's visual baseline, not below the explanation. Render the reflection before foreground text so overlays remain sharp.
- Avoid stacking global darkness filters until the source becomes unreadable; grade layers intentionally.
- Preserve existing output variants unless the user explicitly requests cleanup.
- Make a Git checkpoint after an accepted milestone when the repository is available.
- Keep a source note for factual quotations and a separate originality note for newly written narration.
- Keep `narration.txt` and explanations in separate files. TTS may read only `narration.txt`; never concatenate explanations into the voice input.
- `narration.txt` is not a hidden long-form script. For the Qingxuguan ink format it is the ordered, exact transcription of visible main captions only. Ignore punctuation when comparing, but require character-for-character equality for all spoken words.
- Run the suite-level `$dao-video/scripts/validate_ink_tts.py` before synthesis and again with `--subtitle` after synthesis. A failed validation is a hard stop; do not render, mix, package, or publish.
- Reuse the black-gold project's proven MiniMax timestamp, manual BGM envelope, release-package, and review rules where they are implementation-independent. Reimplement them locally instead of importing private project state.

## Project recovery

When a conversation is missing, reconstruct progress from file modification times, output version names, registered compositions, and current source constants. Treat the most recent preview as an experiment, not automatically the approved final. Report separately:

- latest source state;
- latest short preview;
- latest complete render;
- latest cover still;
- checks that pass;
- the next likely decision or render.

## References

- Read [references/qingxuguan-confirmed-history.md](references/qingxuguan-confirmed-history.md) before resuming or visually rebuilding the established Qingxuguan preset; it records the user-confirmed canvas, background asset, vertical calligraphy layers, motion, voice, BGM, and reflection parameters recovered from the original project thread.
- Read [references/yunxuguan-content-formulas.md](references/yunxuguan-content-formulas.md) when choosing a topic, writing titles, or structuring narration for this series.
- Read [references/validated-patterns.md](references/validated-patterns.md) when applying the established visual style. Adapt the visual system to the new theme.
- Read [references/copy-origin-and-originality.md](references/copy-origin-and-originality.md) before selecting a topic, attributing a quotation, or drafting narration.
- Read [references/mature-workflow-adoption.md](references/mature-workflow-adoption.md) for the independent-project workflow inherited from the mature black-gold pipeline.
