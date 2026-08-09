#!/usr/bin/env python3
"""将青云观最新发布材料汇总到 05-发布。

固定文件名会被最新版覆盖，因此 05-发布永远是唯一上传入口。
"""
import argparse
import os
import shutil


def copy_latest(src, dst):
    if not os.path.isfile(src):
        raise FileNotFoundError(f"找不到文件: {src}")
    shutil.copy2(src, dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default="03-成片/最终视频.mp4")
    ap.add_argument("--cover-v", default="04-封面/竖版封面.png")
    ap.add_argument("--cover-h", default="04-封面/横版封面.png")
    ap.add_argument("--title", required=True)
    ap.add_argument("--topics", required=True, help="话题文本，如：#道家文化 #人生智慧 #青云观")
    ap.add_argument("--outdir", default="05-发布")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    copy_latest(args.video, os.path.join(args.outdir, "最终上传视频.mp4"))
    copy_latest(args.cover_v, os.path.join(args.outdir, "竖版封面.png"))
    copy_latest(args.cover_h, os.path.join(args.outdir, "横版封面.png"))

    doc = f"# 发布信息\n\n## 标题\n\n{args.title.strip()}\n\n## 话题\n\n{args.topics.strip()}\n"
    with open(os.path.join(args.outdir, "标题与话题.md"), "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"已更新 {args.outdir}：发布文档 + 最终视频 + 横竖封面")


if __name__ == "__main__":
    main()
