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

    checks = {
        "project.root": get(cfg, "project.root", ""),
        "voice.voice_id": get(cfg, "voice.voice_id", ""),
        "audio.bgm_path": get(cfg, "audio.bgm_path", ""),
    }
    for label, value in checks.items():
        configured = bool(value)
        exists = configured and (label == "voice.voice_id" or Path(value).expanduser().exists())
        ok = configured and exists
        print(f"{mark(ok):7} config  {label}")
        if not ok:
            failures.append(label)
            if label == "voice.voice_id":
                hint("填写自己 MiniMax 账号可用的 Voice ID；没有时用 minimax_tts.py --ref-audio 上传已获授权的人声进行克隆。")
            elif label == "audio.bgm_path":
                hint("填写本地有权使用的 BGM 文件；仓库不分发音乐素材。")
            elif label == "project.root":
                hint("填写一个存在且可写的视频项目目录。")

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
