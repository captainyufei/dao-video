#!/usr/bin/env python3
"""把 dao-video 项目导出为剪映专业版（JianyingPro / VideoFusion）草稿箱草稿。

生成 <草稿箱>/<书名>/ 文件夹（draft_info.json + draft_meta_info.json +
materials），打开剪映后会在草稿箱直接看到可编辑项目：4 张配图、旁白、
17 条短字幕、钩子/金句/结尾文字卡。

依赖（自动检测，缺失时给出安装命令）:
  git clone --depth 1 https://github.com/drhema/mcp-cut ~/tools/mcp-cut

用法:
  python3 to_jianying.py --config config_9x16.json \
      --draft-name "图书视频-纳瓦尔宝典" [--open] [--force]
"""
import argparse
import json
import os
import platform as os_platform
import shutil
import subprocess
import sys
from pathlib import Path


JIANYING_DRAFTS = str(
    Path.home() / "Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
)
JIANYING_APP = "/Applications/VideoFusion-macOS.app"
FONT_DIR = f"{JIANYING_APP}/Contents/Resources/Font/SystemFont"
MCP_CUT_REPO = os.environ.get("MCP_CUT_REPO", str(Path.home() / "tools/mcp-cut"))


def fmt_ts(t: float) -> str:
    ms = int(round(t * 1000))
    h, rem = divmod(ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(subs: list[dict]) -> str:
    lines = []
    for i, s in enumerate(subs, 1):
        lines.append(str(i))
        lines.append(f"{fmt_ts(s['start'])} --> {fmt_ts(s['end'])}")
        lines.append(s["text"])
        lines.append("")
    return "\n".join(lines)


def scenes_from_cfg(cfg: dict, dur: float) -> list[tuple[float, float]]:
    subs = cfg["subs"]
    scene_map = cfg["scene_map"]
    out = []
    for gi, (s0, _s1) in enumerate(scene_map):
        st = subs[s0]["start"] if s0 < len(subs) else 0.0
        if gi + 1 < len(scene_map):
            nxt = scene_map[gi + 1][0]
            en = subs[nxt]["start"] if nxt < len(subs) else dur
        else:
            en = dur
        en = max(en, st)
        out.append((st, en - st))
    return out


def register_in_root_cache(folder: Path, info: dict, meta: dict) -> None:
    """把新草稿登记进草稿箱根目录缓存，剪映首页能立刻识别。"""
    root = folder.parent
    cache_path = root / "root_meta_info.json"
    if not cache_path.exists():
        return
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    store = cache.setdefault("all_draft_store", [])
    if any(e.get("draft_fold_path") == str(folder) for e in store):
        return
    cover = folder / "draft_cover.jpg"
    store.append({
        "cloud_draft_cover": False, "cloud_draft_sync": False,
        "draft_cloud_last_action_download": False,
        "draft_cloud_purchase_info": "{\n}\n",
        "draft_cloud_template_id": "",
        "draft_cloud_tutorial_info": "{\n}\n",
        "draft_cloud_videocut_purchase_info": '{"template_type":"","unlock_type":""}',
        "draft_cover": str(cover),
        "draft_fold_path": str(folder),
        "draft_id": meta["draft_id"],
        "draft_is_ai_shorts": False,
        "draft_is_cloud_temp_draft": False,
        "draft_is_invisible": False,
        "draft_is_pippit_draft": False,
        "draft_is_web_article_video": False,
        "draft_json_file": str(folder / "draft_info.json"),
        "draft_name": meta["draft_name"],
        "draft_new_version": info["new_version"],
        "draft_root_path": str(root),
        "draft_timeline_materials_size": 0,
        "draft_type": "",
        "draft_web_article_video_enter_from": "",
        "pippit_avatar_url": "", "pippit_extra_info": "{}",
        "pippit_id": "", "pippit_user_name": "",
        "streaming_edit_draft_ready": False,
        "tm_draft_cloud_completed": "",
        "tm_draft_cloud_entry_id": -1, "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": -1, "tm_draft_cloud_user_id": -1,
        "tm_draft_create": meta["tm_draft_create"],
        "tm_draft_modified": meta["tm_draft_modified"],
        "tm_draft_removed": 0, "tm_duration": meta["tm_duration"],
    })
    cache_path.write_text(json.dumps(cache, separators=(",", ":")),
                          encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="dao-video config.json")
    ap.add_argument("--draft-name", help="草稿名（默认 图书视频-<书名>）")
    ap.add_argument("--drafts-dir", default=JIANYING_DRAFTS, help="剪映草稿箱目录")
    ap.add_argument("--open", action="store_true", help="生成后打开剪映")
    ap.add_argument("--force", action="store_true", help="同名草稿已存在时覆盖")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    name = args.draft_name or f"图书视频-{cfg['book']}"
    base_dir = Path(cfg.get("source_assets", "assets")).resolve()
    audio_path = (base_dir / cfg["audio"]).resolve()
    image_paths = [(base_dir / i).resolve() for i in cfg["images"]]
    portrait = cfg.get("orientation", "portrait") != "landscape"
    W, H = (720, 1280) if portrait else (1920, 1080)
    # 总时长以音频实测为准（字幕可能早于结尾留白结束）
    try:
        dur = float(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(audio_path)]).decode().strip())
    except Exception:
        dur = float(cfg["subs"][-1]["end"])

    if not (Path(MCP_CUT_REPO) / "src" / "mcp_cut").exists():
        sys.exit(
            "缺少 mcp-cut，请先安装：\n"
            "  git clone --depth 1 https://github.com/drhema/mcp-cut ~/tools/mcp-cut"
        )
    os.environ["CAPCUT_DRAFTS_DIR"] = args.drafts_dir
    sys.path.insert(0, str(Path(MCP_CUT_REPO) / "src"))
    import mcp_cut.draft as dd

    # 剪映字体目录（mcp-cut 默认指向 CapCut.app）
    if os.path.exists(FONT_DIR):
        dd._FONTS_BY_LANG["zh"] = f"{FONT_DIR}/zh-hans.ttf"
        dd._FONTS_BY_LANG["zh-hant"] = f"{FONT_DIR}/zh-hans.ttf"

    folder = Path(args.drafts_dir) / name
    if folder.exists():
        if not args.force:
            sys.exit(f"草稿已存在：{folder}\n加 --force 覆盖")
        shutil.rmtree(folder)

    print(f"创建草稿 {name} ...")
    dd.create_draft(name, W, H, 30.0)

    for i, (st, du) in enumerate(scenes_from_cfg(cfg, dur), 1):
        print(f"  图片 {i}: {image_paths[i-1].name} @ {st:.2f}s x {du:.2f}s")
        dd.add_image(name, str(image_paths[i - 1]),
                     duration_seconds=du, start_seconds=st,
                     width=W, height=H, track_index=0)

    print(f"  音频: {audio_path.name}（{dur:.2f}s）")
    dd.add_audio(name, str(audio_path), duration_seconds=dur,
                 start_seconds=0.0, track_index=0)

    # 钩子 / 金句 / 结尾文字卡
    cards = []
    if cfg.get("hook"):
        cards.append(("钩子", cfg["hook"].replace("\n", " "), 0.0,
                      float(cfg.get("hook_end", 4.5)), 64))
    g = cfg.get("golden") or {}
    if g.get("text"):
        cards.append(("金句", g["text"].replace("\n", " "),
                      float(g["start"]), float(g["end"]) - float(g["start"]), 52))
    e = cfg.get("ending") or {}
    if e.get("text"):
        cards.append(("结尾", e["text"].replace("\n", " "),
                      float(e["start"]), float(e["end"]) - float(e["start"]), 56))
    for label, text, st, du, fs in cards:
        print(f"  文字卡[{label}]: {text} @ {st:.2f}s x {du:.2f}s")
        dd.add_text(name, text, duration_seconds=du, start_seconds=st,
                    font_size=fs, color_hex="#FFFFFF", alpha=1.0,
                    x=0.0, y=0.0, scale=1.0, language="zh", bold=True,
                    border_color_hex="#000000", border_width=0.10,
                    border_alpha=1.0, has_shadow=True,
                    shadow_color_hex="#000000", shadow_alpha=0.9,
                    shadow_distance=6.0, line_max_width=0.9, track_index=0)

    # 短字幕（白字黑描边，无底，和出片风格一致）
    srt = folder / "captions.srt"
    srt.write_text(build_srt(cfg["subs"]), encoding="utf-8")
    print(f"  字幕: {len(cfg['subs'])} 条")
    dd.add_captions_from_srt(name, str(srt), style="youtube",
                             font_size=20.0, y=0.30, scale=1.0,
                             language="zh", line_max_width=0.9,
                             track_index=0)

    # 适配剪映专业版 schema：new_version 对齐现有草稿，platform 写当前 App
    info = dd._read_json(folder / "draft_info.json")
    info["new_version"] = "164.0.0"
    mac_ver = os_platform.mac_ver()[0]
    plat = {
        "app_id": 3704, "app_source": "lv", "app_version": "10.8.0",
        "device_id": "0" * 32, "hard_disk_id": "0" * 32,
        "mac_address": "0" * 32, "os": "mac", "os_version": mac_ver,
    }
    info["platform"] = dict(plat)
    info["last_modified_platform"] = dict(plat)
    dd._write_json(folder / "draft_info.json", info)
    meta = dd._read_json(folder / "draft_meta_info.json")
    meta["tm_duration"] = info["duration"]
    dd._write_json(folder / "draft_meta_info.json", meta)
    register_in_root_cache(folder, info, meta)

    # 封面
    cover = folder / "draft_cover.jpg"
    subprocess.run(["ffmpeg", "-y", "-i", str(image_paths[0]), "-vf",
                    f"scale={W}:{H}", "-frames:v", "1", str(cover)],
                   check=True, capture_output=True)

    # 校验
    dd._load(name)
    print(f"\nOK 草稿已生成: {folder}")
    print(f"    时长 {dur:.1f}s · {W}x{H} · 30fps · 4 图 / 1 音频 / {len(cfg['subs'])} 字幕 / {len(cards)} 文字卡")
    if args.open:
        subprocess.Popen(["open", "-a", JIANYING_APP])
        print("已打开剪映，去草稿箱查看（可能需要切一下 tab 刷新）")


if __name__ == "__main__":
    main()
