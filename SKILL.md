---
name: dao-video
description: Create, manage, publish-prep, and review Dao-series Chinese philosophy and traditional-culture videos in selectable black-gold or ink-wash styles. Use for generating or resuming videos, choosing 青云观黑金国风 or 青虚观水墨国风, writing copy, storyboarding, voice-over, subtitles, BGM, covers, release packaging, Douyin/WeChat Channels/Xiaohongshu upload preparation, and 24-hour/72-hour/7-day performance review. Never click a platform's final publish control.
---

# Dao Video

Run one configurable, resumable production system with built-in style presets. Treat checked-in files as the workflow definition and the local `config.yaml` as agent-managed account/device configuration. Keep style selection, onboarding, project state, approvals, audio, packaging, publishing, and review inside this skill. The user describes the desired video; the agent operates the tooling.

## Safety boundary

- Never commit, print, copy, or transmit API keys, cookies, browser profiles, private voice samples, or private account data. The explicitly redistributable bundled assets `assets/voice/default-voice.mp3` and `assets/audio/default-bgm.mp3` are approved exceptions.
- Never redistribute any other music, fonts, competitor videos, or templates without confirmed permission.
- Upload and fill publishing forms only when the user requests it. Stop before every final publish/submit control and hand the browser back to the user.
- Never delete the long-lived Ego Lite publishing Space unless the user explicitly names it and asks for deletion.

## Zero-command onboarding

Do not tell the user to run setup commands, inspect dependencies, copy a template, create `config.yaml`, or edit YAML. Perform onboarding yourself before production:

1. Read [references/setup.md](references/setup.md), inspect the machine and existing project state, and infer the project root and style from the request or current project.
2. Install missing non-privileged Python packages and use available package managers for ordinary runtime dependencies when safe. If installation needs administrator approval or an unsupported operating system, pause with the single exact action the user must complete.
3. If no configuration exists, run `scripts/init_config.py` yourself with inferred values and write the resulting path to the project manifest. Never ask the user to create or edit the file manually.
4. Run `scripts/doctor.py` yourself. Add `--publishing` only when publishing preparation is requested. Resolve every machine-local issue that can be resolved safely without user involvement.
5. Check only the providers required by the selected workflow. Before the first paid generation, verify credentials and present the combined voice/model choice below. Do not upload the default voice or call a paid model until the user answers.
6. If MiniMax is selected and no voice is configured, ask whether the user has a specific voice. If they provide an authorized sample or existing Voice ID, use it. If they say they have no specific voice or choose the default, upload `assets/voice/default-voice.mp3` to their MiniMax account, clone it with API Voice ID `dao-default-voice`, save that ID locally, and continue.
7. If the user says `替换音色`、`更换音色`、`使用我的声音` or otherwise specifies a voice, require an authorized sample or an existing Voice ID, clone/select it, update local configuration, and use it for subsequent narration. Never overwrite the bundled default asset with a user's private sample.
8. If no BGM is configured and the user did not request another track, select `assets/audio/default-bgm.mp3` automatically. If the user says `替换 BGM`、`更换音乐` or specifies another track, update only the local project configuration and keep the bundled default unchanged.
9. If another required user-owned prerequisite is missing, stop before generation and request only that prerequisite in plain language. Examples: log in to the provider, add balance, supply an API key securely, grant model access, or log in to a publishing platform.
10. After the user completes the missing prerequisite, rerun the checks automatically and continue from the saved stage. Do not make the user repeat setup instructions or confirm facts already detected.

Use this blocking response format and omit completed checks:

```text
环境已经自动检查完成。正式生成前请确认 2 项：

1. 配音：MiniMax 音色克隆和后续配音会产生费用。如果你有特定音色，请提供已获授权的 10 秒–5 分钟干净人声，或告诉我 MiniMax 中已有的 Voice ID；如果没有，请回复“使用默认音色”，我会上传内置样本并在你的 MiniMax 账号中完成克隆。
2. 画面：本流程会使用火山方舟 Seedream 生图和 Seedance 视频生成，这两项都会产生费用。请确认已配置 ARK_API_KEY、账户有余额，并已开通当前模型权限。

你可以直接回复：“使用默认音色，Seedream 和 Seedance 已开通，可以继续。”
```

If either credential is missing, replace the corresponding confirmation line with the one concrete setup action required. Record the user's voice choice and paid-generation confirmation in local project state so they are not asked again for every episode. Reconfirm only when changing voice, provider, model, or account.

Never expose internal setup chores as a user checklist. Never invent a project root, account permission, balance, or model entitlement. The bundled default voice ID and default BGM are the only predefined audio defaults.

Read [references/setup.md](references/setup.md) for configuration fields and portability rules. For the maintainer's current local production state, read `references/project-state.md` only when that untracked local file exists; initialize it from [references/project-state.example.md](references/project-state.example.md) when needed.

## Resume before producing

1. Resolve the project root from `DAO_VIDEO_CONFIG` or `--config`.
2. Read the project's own status/manifest before generating anything.
3. Inspect existing copy, prompts, audio configuration, covers, release package, and rendered outputs. Reuse confirmed assets.
4. State the recovered stage and the next irreversible or paid operation.

## Style routing

- Read [references/styles.md](references/styles.md) before writing style-specific copy, prompts, compositions, or covers.
- If the user says `黑金`、`黑金国风`、`青云观`、`黑金道士` or `金色能量`, select `qingyunguan-blackgold`.
- If the user says `水墨`、`水墨国风`、`青虚观`、`书法背景`、`水中倒影` or `魏碑字幕`, select `qingxuguan-ink`.
- If the user names neither style, reuse the current episode/project preset. For a new project with no preset, ask the user to choose `黑金` or `水墨` before visual generation.
- Record the selected style preset in project configuration and the episode manifest.
- Do not mix style systems implicitly. Treat a cross-style combination as one controlled experiment requiring user confirmation.

## Production gates

Use this order and stop at every confirmation gate:

1. **Topic and reference** — identify the source/inspiration and record attribution internally. Do not plagiarize wording or shots.
2. **Copy** — generate an original script, run prohibited-word and similarity checks, then obtain user confirmation.
3. **Storyboard** — create scene prompts or deterministic visual-layer planning from the confirmed narration and selected style.
4. **Still-image gate** — generate an Ark still or render a representative Remotion still, present it for confirmation, and do not animate or fully render rejected visuals.
5. **Voice** — synthesize with the configured MiniMax voice. If none is configured, obtain the first-run voice choice; use a supplied authorized voice or clone the bundled default after the user selects it. Switch only when the user explicitly requests replacement.
6. **Video** — generate clips or render the selected composition only after still approval. Size the result from actual narration duration plus required transition overlap.
7. **Edit** — remove source clip audio by default, align subtitles to timestamps from the same TTS generation, apply branding, and mix the selected BGM with the configured manual envelope. Use the bundled default BGM when no replacement is requested.
8. **Cover gate** — build both 3:4 and 4:3 covers from the same approved source frame. Present both before packaging.
9. **Package** — copy only the final video, both confirmed covers, and approved title/topic text into the release directory.
10. **Publish preparation** — follow [references/ego-publish.md](references/ego-publish.md) and stop before final publication.
11. **Performance review** — after the user confirms publication, follow [references/review-loop.md](references/review-loop.md) at the configured checkpoints. Record facts separately from hypotheses and change only one major variable in the next test.

Read [references/workflow.md](references/workflow.md) for commands, audio rules, cover constraints, and implementation pitfalls.
Read [references/review-loop.md](references/review-loop.md) whenever the user asks about results, performance, optimization, next-day adjustments, or whether a prior adjustment worked.

## Presets

- Keep account-specific brand, voice, audio, cover, and publishing values in the agent-managed local `config.yaml`.
- Use `qingyunguan-blackgold` for the established 青云观 black-gold account.
- Use `qingxuguan-ink` for the established 青虚观 manuscript-and-reflection account.
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
