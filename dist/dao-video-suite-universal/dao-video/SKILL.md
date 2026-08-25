---
name: dao-video
description: Orchestrate, manage, and review Dao-series Chinese philosophy/traditional-culture videos across style branches from topic selection through approvals, voice-over, subtitles, BGM, covers, release packaging, publishing handoff, and post-publication experiments. Use for creating or resuming any Dao video project, selecting $dao-blackgold-video or $dao-ink-video, checking prerequisites, preparing Douyin or WeChat Channels uploads, or reviewing 24-hour/72-hour/7-day performance. Never click a platform's final publish control.
---

# Dao Video

Run the shared configurable, resumable production system for every Dao visual branch. Treat checked-in files as the workflow definition and the user's local `config.yaml` as account/device configuration. Route style-specific work to `$dao-blackgold-video` or `$dao-ink-video`; keep project state, approvals, audio, packaging, publishing, and review here.

## Safety boundary

- Never commit, print, copy, or transmit API keys, cookies, browser profiles, cloned-voice source audio, or private account data.
- Never redistribute music, fonts, competitor videos, or templates without confirmed permission.
- Upload and fill publishing forms only when the user requests it. Stop before every final publish/submit control and hand the browser back to the user.
- Never delete the long-lived Ego Lite publishing Space unless the user explicitly names it and asks for deletion.

## First run

1. Read [references/setup.md](references/setup.md) and explicitly tell the user that any selected MiniMax or Ark generation is a paid operation whose current price and balance must be checked. Do not require an unused provider for a branch that does not need it.
2. Install `requirements.txt`, FFmpeg, Node.js, npm, and npx as needed.
3. Run `python3 scripts/init_config.py --output <project>/config.yaml` if no local config exists.
4. For MiniMax, require either a Voice ID already available in the user's own account or an authorized 10-second-to-5-minute voice sample. Guide the user through `minimax_tts.py --ref-audio`; never distribute or suggest the maintainer's clone.
5. When the selected branch uses Ark, require an API key, billing readiness, and confirmed access to the configured copy, Seedream, and Seedance models. Never interpret presence of a key as proof of model entitlement.
6. Ask the user to fill only missing account-specific values. Do not invent a voice ID, BGM path, project root, account, license, or model permission.
7. Install Ego Lite and confirm `ego-browser` only when publishing preparation is requested. Require the user to log in to their own platforms.
8. Run `python3 scripts/doctor.py --config <project>/config.yaml`. Add `--publishing` only when testing publishing.
9. Stop before the first paid generation if cost or permission is still unclear.

Read [references/setup.md](references/setup.md) for configuration fields and portability rules. For the maintainer's current local production state, read `references/project-state.md` only when that untracked local file exists; initialize it from [references/project-state.example.md](references/project-state.example.md) when needed.

## Resume before producing

1. Resolve the project root from `DAO_VIDEO_CONFIG` or `--config`.
2. Read the project's own status/manifest before generating anything.
3. Inspect existing copy, prompts, audio configuration, covers, release package, and rendered outputs. Reuse confirmed assets.
4. State the recovered stage and the next irreversible or paid operation.

## Style routing

- Use `$dao-blackgold-video` for black-gold Taoist figures, golden-energy scenes, Ark-generated cards, and Qingyunguan black-gold covers.
- Use `$dao-ink-video` for manuscript backgrounds, calligraphy parallax, Wei-bei captions, attached water reflections, stone seals, and Qingxuguan ink covers.
- Record the selected style preset in project configuration and the episode manifest.
- Do not mix style systems implicitly. Treat a cross-style combination as one controlled experiment requiring user confirmation.

## Production gates

Use this order and stop at every confirmation gate:

1. **Topic and reference** — identify the source/inspiration and record attribution internally. Do not plagiarize wording or shots.
2. **Copy** — generate an original script, run prohibited-word and similarity checks, then obtain user confirmation.
3. **Storyboard** — create scene prompts or deterministic visual-layer planning from the confirmed narration and selected style.
4. **Still-image gate** — generate an Ark still or render a representative Remotion still, present it for confirmation, and do not animate or fully render rejected visuals.
5. **Voice** — synthesize with the configured MiniMax voice. If the configured clone is unavailable, stop; never silently switch voices. For `qingxuguan-ink`, create an explicit visible-main-caption list and run `scripts/validate_ink_tts.py` before paid TTS and again against the returned subtitle payload; narration must equal the central large captions exactly and must never include bottom explanations or hidden expansion clauses.
6. **Video** — generate clips or render the selected composition only after still approval. Size the result from actual narration duration plus required transition overlap.
7. **Edit** — remove source clip audio by default, align subtitles to timestamps from the same TTS generation, apply branding, and mix BGM with the configured manual envelope.
8. **Cover gate** — build both 3:4 and 4:3 covers from the same approved source frame. Present both before packaging.
9. **Package** — copy only the final video, both confirmed covers, and approved title/topic text into the release directory.
10. **Publish preparation** — follow [references/ego-publish.md](references/ego-publish.md) and stop before final publication.
11. **Performance review** — after the user confirms publication, follow [references/review-loop.md](references/review-loop.md) at the configured checkpoints. Record facts separately from hypotheses and change only one major variable in the next test.

Read [references/workflow.md](references/workflow.md) for commands, audio rules, cover constraints, and implementation pitfalls.
Read [references/review-loop.md](references/review-loop.md) whenever the user asks about results, performance, optimization, next-day adjustments, or whether a prior adjustment worked.

## Presets

- Keep account-specific brand, voice, audio, cover, and publishing values in local `config.yaml`.
- Use `qingyunguan-blackgold` with `$dao-blackgold-video` for the established 青云观 black-gold account.
- Use `qingxuguan-ink` with `$dao-ink-video` for the established 青虚观 manuscript-and-reflection account.
- Never treat a preset as portable authorization for an account-scoped voice, API model, browser profile, font, or music asset.

## Project management

- Store each episode's topic, source, approval state, paid generations, selected assets, final paths, and publishing state in the project manifest.
- Use states such as `copy_pending`, `stills_pending`, `cover_pending`, `ready_to_upload`, `awaiting_publish_confirmation`, and `published`.
- Mark `published` only after the user confirms that publication actually occurred.
- Store platform metrics snapshots and experiment decisions under the project's `06-复盘/` directory. Never overwrite an earlier checkpoint.
- Compare like with like: same platform, similar elapsed time, and preferably similar duration/topic class. Do not compare raw 24-hour data with a 7-day total.
- Separate observed metrics, interpretation, and next action. Treat causal claims as hypotheses unless a controlled follow-up supports them.
- Change one primary variable per episode when testing an adjustment; preserve all other confirmed production settings when practical.
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
