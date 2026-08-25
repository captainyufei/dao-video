#!/usr/bin/env python3
"""Check dao-video prerequisites without making network requests or changing accounts."""
from __future__ import annotations

import argparse
import importlib.util
import os
import platform
import shutil
from pathlib import Path

from dao_config import ark_api_key, config_path, get, load_config


DEFAULT_VOICE_ASSET = Path(__file__).resolve().parent.parent / "assets/voice/default-voice.mp3"
DEFAULT_BGM_ASSET = Path(__file__).resolve().parent.parent / "assets/audio/default-bgm.mp3"


def mark(ok: bool) -> str:
    return "OK" if ok else "MISSING"


def hint(message: str) -> None:
    print(f"        -> {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    parser.add_argument("--publishing", action="store_true", help="同时检查 Ego Lite 发布条件")
    args = parser.parse_args()
    failures: list[str] = []

    path = config_path(args.config)
    cfg = load_config(args.config)
    print(f"config: {path or '未找到（先运行 init_config.py）'}")
    if not path:
        failures.append("config")

    for command in ("python3", "ffmpeg", "ffprobe", "node", "npm", "npx"):
        ok = shutil.which(command) is not None
        print(f"{mark(ok):7} command {command}")
        if not ok:
            failures.append(command)

    for module, package in (("requests", "requests"), ("PIL", "Pillow"), ("yaml", "PyYAML")):
        ok = importlib.util.find_spec(module) is not None
        print(f"{mark(ok):7} python  {package}")
        if not ok:
            failures.append(package)

    ark_ok = bool(ark_api_key())
    print(f"{mark(ark_ok):7} secret  ARK_API_KEY or arkcli profile")
    if not ark_ok:
        failures.append("ARK credentials")
        hint("到火山方舟创建 API Key、开通计费，并设置 ARK_API_KEY；还需单独确认 Seedream/Seedance 模型权限。")
    minimax_ok = bool(os.environ.get("MINIMAX_API_KEY"))
    print(f"{mark(minimax_ok):7} secret  MINIMAX_API_KEY")
    if not minimax_ok:
        failures.append("MINIMAX_API_KEY")
        hint("到 MiniMax 开放平台创建 API Key 并准备可用余额；音色克隆和语音合成可能收费。")

    checks = {"project.root": get(cfg, "project.root", "")}
    for label, value in checks.items():
        configured = bool(value)
        exists = configured and (label == "voice.voice_id" or Path(value).expanduser().exists())
        ok = configured and exists
        print(f"{mark(ok):7} config  {label}")
        if not ok:
            failures.append(label)
            if label == "project.root":
                hint("填写一个存在且可写的视频项目目录。")

    bgm_value = get(cfg, "audio.bgm_path", "")
    if bgm_value:
        bgm_path = Path(bgm_value).expanduser()
        if not bgm_path.is_absolute() and str(bgm_path).startswith("assets/"):
            bgm_path = Path(__file__).resolve().parent.parent / bgm_path
    else:
        bgm_path = DEFAULT_BGM_ASSET
    bgm_ok = bgm_path.exists()
    bgm_state = "默认 BGM" if bgm_path.resolve() == DEFAULT_BGM_ASSET.resolve() else "自定义 BGM"
    print(f"{mark(bgm_ok):7} config  audio.bgm ({bgm_state})")
    if not bgm_ok:
        failures.append("audio.bgm")
        hint("内置默认 BGM 缺失；重新安装 Skill，或让用户明确要求替换 BGM 并提供授权音乐。")

    configured_voice = bool(get(cfg, "voice.voice_id", ""))
    default_voice_ready = DEFAULT_VOICE_ASSET.exists()
    voice_ok = configured_voice or default_voice_ready
    voice_state = "已配置" if configured_voice else "默认音色待自动克隆"
    print(f"{mark(voice_ok):7} config  voice ({voice_state})")
    if not voice_ok:
        failures.append("voice")
        hint("内置默认音色缺失；重新安装 Skill，或让用户明确要求替换音色并提供授权样本。")

    if args.publishing or get(cfg, "publishing.enabled", False):
        ego_app = Path("/Applications/ego lite.app")
        ok = platform.system() == "Darwin" and ego_app.exists()
        print(f"{mark(ok):7} app     Ego Lite")
        if not ok:
            failures.append("Ego Lite")
            hint("按 https://www.egolite.app/document/en/docs/quick-start 安装 macOS 应用，并确认 ego-browser Skill 可用。")
        safe_stop = get(cfg, "publishing.stop_before_publish", True) is True
        print(f"{mark(safe_stop):7} safety  stop_before_publish")
        if not safe_stop:
            failures.append("stop_before_publish")

    if failures:
        print("\n预检未通过: " + ", ".join(failures))
        raise SystemExit(1)
    print("\n预检通过。模型权限和平台登录需在首次实际调用时确认。")


if __name__ == "__main__":
    main()
