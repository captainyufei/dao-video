---
name: dao-video
description: Produce and manage short-form Chinese philosophy/traditional-culture videos from topic selection through copy, storyboard, AI visuals, MiniMax voice-over, subtitles, BGM envelope, covers, release packaging, and Ego Lite form preparation. Use for creating daily videos, resuming a saved video project, checking production prerequisites, preparing Douyin or WeChat Channels uploads, or managing the Qingyunguan preset. Never click a platform's final publish control.
---

# Dao Video

Run a configurable, resumable video-production project. Treat checked-in files as the workflow definition and the user's local `config.yaml` as account/device configuration.

## Safety boundary

- Never commit, print, copy, or transmit API keys, cookies, browser profiles, cloned-voice source audio, or private account data.
- Never redistribute music, fonts, competitor videos, or templates without confirmed permission.
- Upload and fill publishing forms only when the user requests it. Stop before every final publish/submit control and hand the browser back to the user.
- Never delete the long-lived Ego Lite publishing Space unless the user explicitly names it and asks for deletion.

## First run

1. Run `python3 scripts/init_config.py --output <project>/config.yaml` if no local config exists.
2. Ask the user to fill only missing account-specific values. Do not invent a voice ID, BGM path, project root, account, or license.
3. Install `requirements.txt`, FFmpeg, Node.js, npm, and npx as needed.
4. Run `python3 scripts/doctor.py --config <project>/config.yaml`. Add `--publishing` only when testing publishing.
5. Treat model entitlement and platform login as runtime checks; never interpret presence of an API key as proof of access.

Read [references/setup.md](references/setup.md) for configuration fields and portability rules. For the maintainer's current local production state, read `references/project-state.md` only when that untracked local file exists; initialize it from [references/project-state.example.md](references/project-state.example.md) when needed.

## Resume before producing

1. Resolve the project root from `DAO_VIDEO_CONFIG` or `--config`.
2. Read the project's own status/manifest before generating anything.
3. Inspect existing copy, prompts, audio configuration, covers, release package, and rendered outputs. Reuse confirmed assets.
4. State the recovered stage and the next irreversible or paid operation.

## Production gates

Use this order and stop at every confirmation gate:

1. **Topic and reference** — identify the source/inspiration and record attribution internally. Do not plagiarize wording or shots.
2. **Copy** — generate an original script, run prohibited-word and similarity checks, then obtain user confirmation.
3. **Storyboard** — create scene prompts and duration planning from the confirmed narration.
4. **Still-image gate** — generate stills, present them for user confirmation, and do not animate rejected images.
5. **Voice** — synthesize with the configured MiniMax voice. If the configured clone is unavailable, stop; never silently switch voices.
6. **Video** — generate clips only after still approval. Size clip durations from the actual narration duration plus transition overlap.
7. **Edit** — remove source clip audio by default, align subtitles to timestamps from the same TTS generation, apply branding, and mix BGM with the configured manual envelope.
8. **Cover gate** — build both 3:4 and 4:3 covers from the same approved source frame. Present both before packaging.
9. **Package** — copy only the final video, both confirmed covers, and approved title/topic text into the release directory.
10. **Publish preparation** — follow [references/ego-publish.md](references/ego-publish.md) and stop before final publication.

Read [references/workflow.md](references/workflow.md) for commands, audio rules, cover constraints, and implementation pitfalls.

## Default Qingyunguan preset

Use the `qingyunguan` preset only when the user is working on that account/project:

- Visuals: 16:9 black-and-gold Chinese line-art, young Taoist figure; keep video imagery separate from the blue-white cover system.
- Brand: cinnabar `青云观` seal at upper left and the configured cultural-sharing disclaimer at upper right.
- Voice: read `voice.voice_id`; the maintainer's account currently uses an account-scoped clone, not a portable public voice.
- Audio: normalize BGM around −20 LUFS; use no sidechain ducking. Raise the intro, hold a lower constant body level, raise the outro, then fade out.
- Environment sound: remove generated-clip audio unless the config explicitly opts in.
- Publishing: use one persistent Ego Lite Space named by `publishing.ego_space_name`; Douyin and WeChat Channels use two tabs in that Space.

## Project management

- Store each episode's topic, source, approval state, paid generations, selected assets, final paths, and publishing state in the project manifest.
- Use states such as `copy_pending`, `stills_pending`, `cover_pending`, `ready_to_upload`, `awaiting_publish_confirmation`, and `published`.
- Mark `published` only after the user confirms that publication actually occurred.
- Preserve rejected or experimental outputs outside the release directory and never mistake them for finals.

## Tool routing

- Use `scripts/ark_llm.py`, `ark_images.py`, and `ark_video.py` for direct Volcengine Ark API calls. Supply `ARK_API_KEY`; never scrape arkcli identity directories.
- Use `scripts/minimax_tts.py` with `MINIMAX_API_KEY` and configured `voice.voice_id`.
- Use `scripts/make_srt.py`, `render_subs.py`, `make_final.py`, and `package_release.py` for deterministic post-production.
- Treat `gen_images.py` as an optional legacy DashScope path, not the Qingyunguan default.
- Treat Jianying export as optional and macOS-specific. Prefer `to_jianying.py`; do not use the legacy pyJianYingDraft path for current Jianying versions.

## Completion criteria

Report completion only after relevant validation passes:

- `doctor.py` passes for the requested scope.
- Script syntax and Skill validation pass.
- Video probe confirms playable video/audio streams, intended dimensions, and expected duration.
- Both release covers visibly match their official source files.
- Publishing forms are filled and handed off, with no final publish action triggered.
