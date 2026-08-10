#!/usr/bin/env python3
"""Create an agent-managed dao-video configuration from the committed example."""
import argparse
import shutil
from pathlib import Path

from dao_config import SKILL_ROOT


def set_value(data: dict, section: str, key: str, value: str | None) -> None:
    if value is not None:
        data.setdefault(section, {})[key] = value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="config.yaml")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--project-root")
    parser.add_argument("--preset", choices=("qingyunguan-blackgold", "qingxuguan-ink"))
    parser.add_argument("--brand-name")
    parser.add_argument("--voice-id")
    parser.add_argument("--bgm-path")
    parser.add_argument("--ego-space-name")
    args = parser.parse_args()
    output = Path(args.output).expanduser().resolve()
    if output.exists() and not args.force:
        raise SystemExit(f"配置已存在: {output}（如需覆盖，加 --force）")
    output.parent.mkdir(parents=True, exist_ok=True)

    values_supplied = any(
        value is not None
        for value in (
            args.project_root,
            args.preset,
            args.brand_name,
            args.voice_id,
            args.bgm_path,
            args.ego_space_name,
        )
    )
    if values_supplied:
        try:
            import yaml
        except ImportError as exc:
            raise SystemExit("缺少 PyYAML；请由 Agent 安装 requirements.txt 后重试。") from exc
        data = yaml.safe_load((SKILL_ROOT / "config.example.yaml").read_text(encoding="utf-8")) or {}
        set_value(data, "project", "root", args.project_root)
        set_value(data, "project", "preset", args.preset)
        set_value(data, "project", "brand_name", args.brand_name)
        set_value(data, "voice", "voice_id", args.voice_id)
        set_value(data, "audio", "bgm_path", args.bgm_path)
        set_value(data, "publishing", "ego_space_name", args.ego_space_name)
        output.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    else:
        shutil.copyfile(SKILL_ROOT / "config.example.yaml", output)
    print(f"已创建本地配置: {output}")
    print("配置由 Agent 管理；接下来由 Agent 运行 doctor.py 并只向用户报告无法自动补齐的条件。")


if __name__ == "__main__":
    main()
