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
    minimax_ok = bool(os.environ.get("MINIMAX_API_KEY"))
    print(f"{mark(minimax_ok):7} secret  MINIMAX_API_KEY")
    if not minimax_ok:
        failures.append("MINIMAX_API_KEY")

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

    if args.publishing or get(cfg, "publishing.enabled", False):
        ego_app = Path("/Applications/ego lite.app")
        ok = platform.system() == "Darwin" and ego_app.exists()
        print(f"{mark(ok):7} app     Ego Lite")
        if not ok:
            failures.append("Ego Lite")
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
