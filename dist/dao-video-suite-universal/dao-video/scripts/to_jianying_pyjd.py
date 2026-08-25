#!/usr/bin/env python3
"""基于 pyJianYingDraft（GuanYixuan/pyJianYingDraft）的剪映草稿导出器。

与 to_jianying.py（mcp-cut）的区别：
  - 按 pyJianYingDraft 的方式生成 draft_content.json（new_version 110）
  - 素材直接引用原文件绝对路径（不复制进草稿）
  - 字幕用 import_srt 转为文本片段
  - 补上 pyJianYingDraft 没做的 meta 登记（draft_name/时长/封面/根缓存）

用法:
  python3 to_jianying_pyjd.py --config config_9x16.json \
      --draft-name "图书视频-纳瓦尔宝典-pyd" [--open]

依赖:
  pip install pyJianYingDraft
"""
import argparse
import json
import os
import platform as os_platform
import shutil
import subprocess
import uuid
from pathlib import Path

import pyJianYingDraft as draft
from pyJianYingDraft import ClipSettings, TextStyle, trange


JIANYING_DRAFTS = str(
    Path.home() / "Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
)
JIANYING_APP = "/Applications/VideoFusion-macOS.app"


def fmt_ts(t: float) -> str:
    ms = int(round(t * 1000))
    h, rem = divmod(ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(subs: list[dict]) -> str:
    lines = []
    for i, s in enumerate(subs, 1):
        lines += [str(i), f"{fmt_ts(s['start'])} --> {fmt_ts(s['end'])}", s["text"], ""]
    return "\n".join(lines)


def scenes_from_cfg(cfg: dict, dur: float) -> list[tuple[float, float]]:
    subs, scene_map = cfg["subs"], cfg["scene_map"]
    out = []
    for gi, (s0, _s1) in enumerate(scene_map):
        st = subs[s0]["start"] if s0 < len(subs) else 0.0
        en = (subs[scene_map[gi + 1][0]]["start"]
              if gi + 1 < len(scene_map) else dur)
        en = max(en, st)
        out.append((st, en - st))
    return out


def register_in_root_cache(folder: Path, info: dict, meta: dict) -> None:
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
        "draft_cover": str(cover), "draft_fold_path": str(folder),
        "draft_id": meta["draft_id"], "draft_is_ai_shorts": False,
        "draft_is_cloud_temp_draft": False, "draft_is_invisible": False,
        "draft_is_pippit_draft": False, "draft_is_web_article_video": False,
        "draft_json_file": str(folder / "draft_content.json"),
        "draft_name": meta["draft_name"],
        "draft_new_version": info.get("new_version", ""),
        "draft_root_path": str(root),
        "draft_timeline_materials_size": 0, "draft_type": "",
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
    ap.add_argument("--config", required=True)
    ap.add_argument("--draft-name", help="草稿名（默认 图书视频-<书名>-pyd）")
    ap.add_argument("--drafts-dir", default=JIANYING_DRAFTS)
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    name = args.draft_name or f"图书视频-{cfg['book']}-pyd"
    base_dir = Path(cfg.get("source_assets", "assets")).resolve()
    audio_path = (base_dir / cfg["audio"]).resolve()
    image_paths = [(base_dir / i).resolve() for i in cfg["images"]]
    portrait = cfg.get("orientation", "portrait") != "landscape"
    W, H = (720, 1280) if portrait else (1920, 1080)
    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio_path)]).decode().strip())

    folder = draft.DraftFolder(args.drafts_dir)
    script = folder.create_draft(name, W, H, fps=30, allow_replace=True)
    script.append_tracks([
        draft.TrackSpec(draft.TrackType.audio, "voice"),
        draft.TrackSpec(draft.TrackType.video, "main"),
        draft.TrackSpec(draft.TrackType.text, "subtitle"),
        draft.TrackSpec(draft.TrackType.text, "cards"),
    ])

    # 音频
    script.add_segment(
        draft.AudioSegment(str(audio_path), trange("0s", f"{dur:.3f}s")),
        "voice",
    )
    # 图片（按场景时间轴）
    for i, (st, du) in enumerate(scenes_from_cfg(cfg, dur), 1):
        mat = draft.VideoMaterial(str(image_paths[i - 1]))
        seg = draft.VideoSegment(mat, trange(f"{st:.3f}s", f"{du:.3f}s"))
        script.add_segment(seg, "main")

    # 钩子 / 金句 / 结尾文字卡
    cards = []
    if cfg.get("hook"):
        cards.append((cfg["hook"].replace("\n", ""), 0.0,
                      float(cfg.get("hook_end", 4.5))))
    g = cfg.get("golden") or {}
    if g.get("text"):
        cards.append((g["text"].replace("\n", ""), float(g["start"]),
                      float(g["end"]) - float(g["start"])))
    e = cfg.get("ending") or {}
    if e.get("text"):
        cards.append((e["text"].replace("\n", ""), float(e["start"]),
                      float(e["end"]) - float(e["start"])))
    for text, st, du in cards:
        script.add_segment(draft.TextSegment(
            text, trange(f"{st:.3f}s", f"{du:.3f}s"),
            style=TextStyle(size=16.0, bold=True, color=(1.0, 1.0, 1.0),
                            align=1, auto_wrapping=True, max_line_width=0.9),
            clip_settings=ClipSettings(transform_y=0.0),
        ), "cards")

    # 短字幕
    srt = Path(args.drafts_dir) / name / "captions.srt"
    srt.write_text(build_srt(cfg["subs"]), encoding="utf-8")
    script.import_srt(
        str(srt), track_name="subtitle",
        text_style=TextStyle(size=10.0, bold=True, color=(1.0, 1.0, 1.0),
                             align=1, auto_wrapping=False, max_line_width=0.9),
        clip_settings=ClipSettings(transform_y=-0.65),
    )
    script.save()

    # 补 meta（pyJianYingDraft 原样不填）并登记根缓存
    draft_dir_path = Path(args.drafts_dir) / name
    meta_path = draft_dir_path / "draft_meta_info.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["draft_name"] = name
    meta["draft_id"] = str(uuid.uuid4()).upper()
    meta["draft_fold_path"] = str(draft_dir_path)
    meta["draft_root_path"] = str(Path(args.drafts_dir))
    meta["tm_duration"] = int(dur * 1_000_000)
    meta["tm_draft_create"] = int(__import__("time").time() * 1_000_000)
    meta["tm_draft_modified"] = meta["tm_draft_create"]
    cover = draft_dir_path / "draft_cover.jpg"
    subprocess.run(["ffmpeg", "-y", "-i", str(image_paths[0]),
                    "-vf", f"scale={W}:{H}", "-frames:v", "1", str(cover)],
                   check=True, capture_output=True)
    meta["draft_cover"] = str(cover)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1),
                         encoding="utf-8")

    info = json.loads((draft_dir_path / "draft_content.json")
                      .read_text(encoding="utf-8"))
    register_in_root_cache(draft_dir_path, info, meta)

    print(f"OK 草稿已生成（pyJianYingDraft 方式）: {draft_dir_path}")
    print(f"    时长 {dur:.1f}s · {W}x{H} · 30fps · {len(image_paths)} 图 / 1 音频 / "
          f"{len(cfg['subs'])} 字幕 / {len(cards)} 文字卡")
    print(f"    文件: draft_content.json (new_version={info.get('new_version')}) + draft_meta_info.json")
    if args.open:
        subprocess.Popen(["open", "-a", JIANYING_APP])
        print("已打开剪映，去草稿箱对比两个草稿")


if __name__ == "__main__":
    main()
