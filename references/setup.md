# Setup and portability

This is an agent execution reference, not a user checklist. The agent must run checks, create configuration, and perform safe local setup. Ask the user only for prerequisites that require their identity, authorization, payment decision, licensed asset, or interactive login.

## Required software

- Python 3
- FFmpeg and ffprobe
- Node.js, npm, and npx
- Python packages from `requirements.txt`

Optional components:

- Ego Lite for browser-assisted publishing
- Jianying Pro and `mcp-cut` for editable draft export on macOS
- faster-whisper for third-party audio alignment fallback

## Cost and account notice

- MiniMax voice cloning and synthesis are paid API operations. Require the user to review current pricing and maintain usable balance before cloning or synthesis.
- Volcengine Ark copy, Seedream image generation, and Seedance video generation are paid model calls. Require the user to confirm model entitlement and current pricing before the first generation.
- Never state a hard-coded price as permanent. Link to the provider's current pricing page and treat every paid call as visible project work.
- Ego Lite is only required for publishing preparation. Platform accounts, verification, and login are user responsibilities.

Before the first paid generation, present one combined confirmation instead of separate technical checklists:

1. Ask whether the user wants to provide a specific authorized voice or use the bundled default voice.
2. State explicitly that the visual workflow uses Seedream for still images and Seedance for video generation, both are paid Ark calls, and require API credentials, balance, and model entitlement.
3. Wait for the user's choice/confirmation before uploading the default voice or calling Seedream/Seedance.
4. Save the confirmation locally and do not repeat it for every episode unless the voice, provider, model, or account changes.

## MiniMax first-time voice setup

1. Create a MiniMax API key at `https://platform.minimaxi.com/` and add usable balance or a suitable plan.
2. When no voice is configured, first ask whether the user has a specific authorized voice. Use `assets/voice/default-voice.mp3` only after the user says they have no specific voice or selects the default. Upload it to the user's own MiniMax account and clone it as API Voice ID `dao-default-voice`; the user-facing name remains “默认音色”.
3. Save the successful Voice ID in local `config.yaml` and reuse it. Do not upload or clone again on every episode.
4. When the user asks to `替换音色` or supplies a specific voice, require an authorized sample in mp3, m4a, or wav format, 10 seconds to 5 minutes, no more than 20 MB, or accept an existing Voice ID from that user's MiniMax account.
5. For a replacement clone, choose a new API Voice ID 8–256 characters long, starting with a letter, containing only letters, digits, `-`, and `_`, and not ending with `-` or `_`. Keep private replacement samples outside the repository.
6. Agent-run example for replacing the voice:

```bash
python3 scripts/minimax_tts.py \
  --ref-audio /path/to/authorized-voice.wav \
  --voice-id my-dao-voice-01 \
  --text /path/to/test-narration.txt \
  --output /path/to/test-narration.wav \
  --subtitle
```

7. Save the successful replacement Voice ID to local `config.yaml`. Remind the user that the provider may remove a cloned voice if it is not formally used within its documented retention window.

Official references:

- Voice clone guide: `https://platform.minimaxi.com/docs/guides/speech-voice-clone`
- Voice clone API: `https://platform.minimaxi.com/docs/api-reference/voice-cloning-clone`
- Current pricing: `https://platform.minimaxi.com/docs/guides/pricing-paygo`

## Volcengine Ark first-time setup

1. Register and complete any required account verification.
2. Enable billing and check usable balance.
3. Create an API key at `https://console.volcengine.com/ark/region:ark+cn-beijing/apikey`.
4. Confirm entitlement for the configured copy model, Seedream model, and Seedance model. An API key alone is insufficient proof.
5. Export `ARK_API_KEY` or sign in with arkcli. Use direct model-ID API calls; do not create an endpoint solely because arkcli asks for `ep-...`.
6. If a model is unavailable, stop and ask the user to select an entitled model after reviewing its price.

## Ego Lite first-time setup

1. Install the macOS app from `https://www.egolite.app/document/en/docs/quick-start`.
2. Complete onboarding and optionally migrate Chrome data when the user wants to reuse local logins.
3. Confirm the `ego-browser` Skill is installed; otherwise run `npx skills add citrolabs/ego-lite`.
4. Ask the user to log in to Douyin and WeChat Channels inside Ego Lite.
5. Reuse one persistent Space with two platform tabs. Never delete it automatically and never click the final publish control.

## Secrets

Provide secrets through environment variables or a secret manager:

- `ARK_API_KEY`: copy, Seedream, and Seedance direct API calls. If absent, scripts may read the API key from arkcli's selected profile without assuming an identity name.
- `MINIMAX_API_KEY`: voice cloning and synthesis
- `DASHSCOPE_API_KEY`: legacy image-generation path only
- `REDFOX_API_KEY`: optional reference-video retrieval only

Never put real values in `config.yaml`, `.env.example`, Git history, logs, or screenshots.

## Local configuration

Copy `config.example.yaml` to a project-local `config.yaml`. The committed example must contain no user-specific absolute paths or working voice IDs.

Required for the complete Qingyunguan workflow:

- `project.root`: writable project directory
- `voice.voice_id`: a voice available to the configured MiniMax account
- `audio.bgm_path`: a locally licensed audio file
- `cover.frame_vertical`: local approved cover frame when using the legacy template composer

Publishing remains disabled by default. Enabling it does not prove that platform accounts are logged in.

## Portability guarantees

- A cloned MiniMax voice ID is account-scoped. Each recipient's Agent uploads the bundled default sample into that recipient's account; the Skill does not share a cloud voice across accounts.
- Ego Lite Spaces, cookies, and platform logins are local browser state and never travel with this repository.
- Paid model IDs may require separate entitlement and may change. Prefer the configured ID and report access errors rather than changing models silently.
- Use the approved bundled `assets/audio/default-bgm.mp3` when the user does not request another track. Treat every replacement BGM and font as user-supplied; do not commit it unless its license explicitly permits redistribution.
- Jianying paths are derived from the current home directory or explicit flags; they are not portable across operating systems.

## Agent-run first initialization

Run these commands yourself. Do not paste them as required work for the user:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/init_config.py --output /path/to/project/config.yaml
export DAO_VIDEO_CONFIG=/path/to/project/config.yaml
python3 scripts/doctor.py
```

Add `--publishing` to the last command only when Ego Lite publishing is in scope.
