# Mature workflow adoption

Use the established black-gold/`dao-video` workflow as an operational reference while keeping the ink project independent.

## Adopt immediately

### Local configuration

Keep a local, uncommitted `config.yaml` or equivalent with:

- project root and `qingxuguan-ink` preset;
- authorized MiniMax voice ID and emotion/speed;
- BGM source and loudness/envelope values;
- font and manuscript asset paths;
- publishing settings and stop-before-publish policy;
- review checkpoints.

Never read another project's private config as a runtime dependency.

### Episode state

Keep one manifest per episode with:

- topic, source notes, script, title, and selected style;
- approval state for copy, representative still, voice, full video, and covers;
- paid generations and selected asset paths;
- final video, cover, and release-package paths;
- publishing state and metrics checkpoints.

Use at least these states:

```text
copy_pending
still_pending
voice_pending
render_pending
cover_pending
ready_to_upload
awaiting_publish_confirmation
published
```

Mark `published` only after user confirmation.

### Confirmation gates

Use this order:

1. Confirm topic, source boundary, and original script.
2. Render and confirm one representative still.
3. Confirm voice and emotion before the final synthesis when a paid call is involved.
4. Render a 5–6 second motion sample.
5. Render and inspect the full video.
6. Confirm feed covers at full and thumbnail sizes.
7. Package the release; do not publish automatically.

Do not spend on rejected upstream work.

### Timing and audio

- Generate final narration before locking picture duration.
- Prefer timestamps from the same MiniMax synthesis call.
- Use Whisper alignment only as a fallback for third-party audio.
- Store semantic BGM transition times in an episode-local audio config.
- Use a manual envelope: stronger intro, lower stable body, rising outro, final fade.
- Change voice, BGM, loudness, or envelope one primary variable at a time during testing.

### Release package

Keep only approved release assets in the release directory:

- final upload video;
- confirmed 3:4 cover;
- confirmed 4:3 cover when the target platform needs it;
- approved title, description, and no more than five deduplicated topics;
- episode manifest or release record.

Keep experiments and rejected versions outside the release directory.

### Review loop

Record comparable snapshots around 24 hours, 72 hours, and 7 days when data is available. Separate:

1. observed facts;
2. interpretation;
3. next controlled change.

Compare the same platform at similar elapsed time and similar topic/duration class. Treat causal explanations as hypotheses until a controlled next episode supports them.

## Keep ink-specific

Do not copy these black-gold implementation choices:

- Ark still/video generation requirement;
- recurring Taoist character consistency;
- black-and-gold prompt language;
- character-centric cover cropping;
- black-gold palette and energy effects.

Keep these inside the ink project:

- Remotion renderer and compositions;
- manuscript, large-glyph, parallax, and water-reflection layers;
- Wei-bei foreground captions and Song-style explanations;
- dedicated feed-cover composition and irregular stone seal;
- licensed local fonts, manuscript images, voice samples, and generated music.

## Validation threshold

Do not call the ink pipeline mature after one accepted example. Require at least three repeatable episodes, preferably five, that meet all of these conditions:

- new copy and timings can be substituted without code breakage;
- captions stay aligned and legible across different lengths;
- voice and BGM remain balanced;
- full video and covers export reliably;
- release packages contain only accepted assets;
- post-publication metrics are recorded consistently;
- recovery from a fresh session works from config and manifest rather than conversation memory.

Only after this threshold should common implementation code be considered for extraction or repository merging.
