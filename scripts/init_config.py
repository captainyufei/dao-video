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
    print("请至少填写 project.root、voice.voice_id 和 audio.bgm_path，然后运行 doctor.py。")


if __name__ == "__main__":
    main()
