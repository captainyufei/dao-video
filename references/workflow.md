# Production reference

## Direct API commands

```bash
python3 scripts/ark_llm.py --config "$DAO_VIDEO_CONFIG" --topic "主题" --out narration.txt
python3 scripts/ark_images.py --config "$DAO_VIDEO_CONFIG" --prompts prompts.txt --outdir assets --scene 围合
python3 scripts/ark_video.py --config "$DAO_VIDEO_CONFIG" --images assets/img-01.png,assets/img-02.png --outdir video
python3 scripts/minimax_tts.py --config "$DAO_VIDEO_CONFIG" --text narration.txt --output assets/narration.wav --subtitle
```

## Timing and subtitles

- Generate narration before video clips.
- Use MiniMax timestamps from the same synthesis call whenever available.
- Use whisper segment interpolation only as a fallback for third-party audio.
- Ensure total picture duration covers narration plus transition overlap.
- When looping subtitle PNG inputs in FFmpeg, set a finite duration and use `-shortest`.
- Supply FFmpeg overlay enable times as seconds, not `HH:MM:SS` strings.

## Audio

- Do not use automatic ducking for the Qingyunguan preset.
- Normalize BGM with linear loudness mode to avoid latency.
- Apply a manual envelope: prominent intro, constant lower body, rising outro, final fade.
- Keep semantic transition times in each episode's `audio-config.json`.
- Remove source video audio by default.
- If a sidechain experiment is explicitly requested, split a voice label before feeding multiple consumers; never reuse one label twice.

## Visuals

- The Qingyunguan video default is black-and-gold line art on a dark background.
- Describe the recurring Taoist figure as young, refined, and consistent across scenes.
- Use scene prefixes `远景|`, `近景|`, or `围合|` with `ark_images.py`.
- Do not mix cover palette instructions into video-frame prompts.

## Covers

- Prefer one clean frame from the current unbranded video as the source for both covers.
- Allow mirroring, proportional scaling, and focus crop; never stretch or redraw the person without explicit permission.
- Produce both 3:4 and 4:3 files and verify them independently.
- Keep exact Chinese title and seal rendering local; do not ask an image model to render final Chinese text.
- Treat `make_cover.py` as the legacy transparent-frame composer. Pass `--frame-v` explicitly.

## Packaging

The release directory contains only:

- final upload video
- confirmed 4:3 cover
- confirmed 3:4 cover
- approved title, description, and at most five deduplicated topics

## Known constraints

- MiniMax synthesis supports a 32000 Hz API sample rate in the verified flow; convert the delivered WAV afterward as needed.
- Seedance outputs may need scaling to the final canvas.
- Homebrew FFmpeg builds can omit libass/drawtext; use PIL-rendered subtitle PNG overlays.
- Use the direct Ark HTTP API for model IDs. Do not rely on arkcli endpoint discovery.
