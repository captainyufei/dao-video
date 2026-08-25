#!/usr/bin/env python3
"""Create a local dao-video configuration from the committed example."""
import argparse
import shutil
from pathlib import Path

from dao_config import SKILL_ROOT


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="config.yaml")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    output = Path(args.output).expanduser().resolve()
    if output.exists() and not args.force:
        raise SystemExit(f"配置已存在: {output}（如需覆盖，加 --force）")
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SKILL_ROOT / "config.example.yaml", output)
    print(f"已创建本地配置: {output}")
    print("下一步：")
    print("1. MiniMax：创建 API Key 并准备余额；填写自己账号已有的 voice_id，或用已获授权的人声运行 minimax_tts.py --ref-audio 克隆。")
    print("2. 火山方舟：创建 API Key、开通计费，并确认文案、Seedream、Seedance 模型权限。")
    print("3. 填写 project.root、voice.voice_id 和有权使用的 audio.bgm_path。")
    print("4. 需要自动填写发布页面时，安装 Ego Lite 并登录自己的抖音/视频号账号。")
    print("5. 运行 doctor.py；发布功能再加 --publishing。")


if __name__ == "__main__":
    main()
