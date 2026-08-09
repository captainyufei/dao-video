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
