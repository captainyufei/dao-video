#!/usr/bin/env python3
"""方舟 Seedance 图生视频 — 每张静态图 → 5-10 秒动态视频
用法: ark_video.py --images img-01.png,img-02.png --outdir video --motion "动作描述"
"""
import argparse, base64, json, os, sys, time
import requests
from dao_config import ark_api_key, get, load_config

DEFAULT_MOTION = ("画面缓慢推近，人物衣袂与飘带微微飘动，云雾缓缓流动，"
                  "光影柔和变化，电影感运镜，静谧空灵")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True, help="逗号分隔的图片路径")
    ap.add_argument("--outdir", default="video")
    ap.add_argument("--motion", default=DEFAULT_MOTION)
    ap.add_argument("--duration", type=int, default=5)
    ap.add_argument("--model")
    ap.add_argument("--config")
    args = ap.parse_args()
    cfg = load_config(args.config)
    key = ark_api_key()
    if not key:
        sys.exit("错误: 未找到 ARK_API_KEY 环境变量")
    model = args.model or get(cfg, "models.seedance", "doubao-seedance-2-0-fast-260128")
    BASE = "https://ark.cn-beijing.volces.com/api/v3"
    H = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    os.makedirs(args.outdir, exist_ok=True)
    images = [p.strip() for p in args.images.split(",") if p.strip()]
    for idx, img in enumerate(images, 1):
        b64 = base64.b64encode(open(img, "rb").read()).decode()
        r = requests.post(f"{BASE}/contents/generations/tasks", headers=H, json={
            "model": model,
            "content": [{"type": "text", "text": args.motion},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}],
            "duration": args.duration,
        }, timeout=60)
        d = r.json()
        if r.status_code != 200:
            print(f"❌ {img}: {json.dumps(d, ensure_ascii=False)[:200]}"); continue
        task = d["id"]
        print(f"[{idx}/{len(images)}] 任务 {task} 生成中（约 3-5 分钟）...")
        for i in range(60):
            time.sleep(10)
            r2 = requests.get(f"{BASE}/contents/generations/tasks/{task}", headers=H, timeout=30)
            st = r2.json().get("status")
            if st == "succeeded":
                url = r2.json()["content"]["video_url"]
                out = os.path.join(args.outdir, f"clip-{idx:02d}.mp4")
                open(out, "wb").write(requests.get(url, timeout=120).content)
                print(f"  -> {out}")
                break
            if st in ("failed", "cancelled"):
                print(f"  ❌ 任务失败: {r2.text[:200]}"); break

if __name__ == "__main__":
    main()
