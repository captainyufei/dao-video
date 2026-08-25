#!/usr/bin/env python3
"""Portable configuration and credential helpers for dao-video."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent


def config_path(explicit: str | None = None) -> Path | None:
    candidates = [explicit, os.environ.get("DAO_VIDEO_CONFIG")]
    for item in candidates:
        if item:
            path = Path(item).expanduser().resolve()
            if path.exists():
                return path
            raise FileNotFoundError(f"配置文件不存在: {path}")
    for name in ("config.yaml", "config.yml", "config.json"):
        path = Path.cwd() / name
        if path.exists():
            return path.resolve()
    return None


def load_config(explicit: str | None = None) -> dict[str, Any]:
    path = config_path(explicit)
    if path is None:
        return {}
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("读取 YAML 配置需要安装 PyYAML: python3 -m pip install PyYAML") from exc
    data = yaml.safe_load(text)
    return data or {}


def get(cfg: dict[str, Any], dotted: str, default: Any = None) -> Any:
    value: Any = cfg
    for key in dotted.split("."):
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


def ark_api_key() -> str | None:
    """Prefer the environment; otherwise read arkcli's selected profile generically."""
    key = os.environ.get("ARK_API_KEY") or os.environ.get("VOLCENGINE_ARK_API_KEY")
    if key:
        return key
    arkcli_config = Path.home() / ".arkcli/config.yaml"
    if not arkcli_config.exists():
        return None
    try:
        import yaml
        data = yaml.safe_load(arkcli_config.read_text(encoding="utf-8")) or {}
        profile_name = data.get("default_profile")
        profile = (data.get("profiles") or {}).get(profile_name, {})
        return profile.get("api_key")
    except (OSError, ValueError, TypeError):
        return None


def expand_path(value: str | None) -> str:
    return str(Path(value).expanduser().resolve()) if value else ""
