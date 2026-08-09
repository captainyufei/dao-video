# Setup and portability

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

## MiniMax first-time voice setup

1. Create a MiniMax API key at `https://platform.minimaxi.com/` and add usable balance or a suitable plan.
2. Require an authorized voice sample in mp3, m4a, or wav format, 10 seconds to 5 minutes, no more than 20 MB.
3. Never offer or distribute the maintainer's cloned voice, source recording, or Voice ID. Require each recipient to use a voice available in their own account.
4. Choose a custom Voice ID 8–256 characters long, starting with a letter, containing only letters, digits, `-`, and `_`, and not ending with `-` or `_`.
5. Run:

```bash
python3 scripts/minimax_tts.py \
  --ref-audio /path/to/authorized-voice.wav \
  --voice-id my-dao-voice-01 \
  --text /path/to/test-narration.txt \
  --output /path/to/test-narration.wav \
  --subtitle
```

6. Save the successful Voice ID to local `config.yaml`. Remind the user that the provider may remove a cloned voice if it is not formally used within its documented retention window.

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

- A cloned MiniMax voice ID is normally account-scoped. Recipients must clone or choose their own permitted voice.
- Ego Lite Spaces, cookies, and platform logins are local browser state and never travel with this repository.
- Paid model IDs may require separate entitlement and may change. Prefer the configured ID and report access errors rather than changing models silently.
- BGM and fonts are user-supplied assets. Do not bundle them unless their license explicitly permits redistribution.
- Jianying paths are derived from the current home directory or explicit flags; they are not portable across operating systems.

## First-run commands

```bash
python3 -m pip install -r requirements.txt
python3 scripts/init_config.py --output /path/to/project/config.yaml
export DAO_VIDEO_CONFIG=/path/to/project/config.yaml
python3 scripts/doctor.py
```

Add `--publishing` to the last command only when Ego Lite publishing is in scope.
