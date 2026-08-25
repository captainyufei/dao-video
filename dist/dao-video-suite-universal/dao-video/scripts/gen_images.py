#!/usr/bin/env python3
"""图书号视频配图生成器 — DashScope 万相 wanx2.1-t2i-turbo
用法:
  gen_images.py --prompts prompts.txt --outdir assets [--size 1920x1080|720x1280]
prompts.txt 每行一个场景提示词（脚本自动附加统一风格前缀）
"""
import argparse, os, sys, time, json
import requests

API = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
STYLE_PREFIX = "温暖晨光、柔和电影感二维插画、安静治愈氛围、细腻线条与柔和上色、电影构图、画面中没有任何文字、没有水印"
ALLOWED = {"720x1280", "1280x720", "1024x1024", "1920x1080", "1080x1920"}

def submit(prompt, size, key):
    r = requests.post(API, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }, json={"model": "wanx2.1-t2i-turbo", "input": {"prompt": prompt},
             "parameters": {"size": size, "n": 1}}, timeout=60)
    d = r.json()
    task = d.get("output", {}).get("task_id", "")
    if not task:
        raise RuntimeError(f"提交失败: {d}")
    return task

def poll(task, key, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = requests.get(f"https://dashscope.aliyuncs.com/api/v1/tasks/{task}",
                         headers={"Authorization": f"Bearer {key}"}, timeout=30)
        d = r.json()
        st = d.get("output", {}).get("task_status", "")
        if st == "SUCCEEDED":
            return d["output"]["results"][0]["url"]
        if st == "FAILED":
            raise RuntimeError(f"生成失败: {json.dumps(d, ensure_ascii=False)[:300]}")
        time.sleep(5)
    raise TimeoutError("生成超时")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", required=True, help="每行一个场景提示词")
    ap.add_argument("--outdir", default="assets")
    ap.add_argument("--size", default="1920x1080", choices=sorted(ALLOWED))
    ap.add_argument("--style", default=STYLE_PREFIX)
    args = ap.parse_args()
    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        sys.exit("错误: 需要环境变量 DASHSCOPE_API_KEY")
    # 万相 wanx2.1-t2i-turbo 支持尺寸：1024*1024 / 720*1280 / 1280*720
    size_map = {"1920x1080": "1280*720", "720x1280": "720*1280", "1024x1024": "1024*1024"}
    size = size_map[args.size]
    prompts = [l.strip() for l in open(args.prompts, encoding="utf-8") if l.strip()]
    os.makedirs(args.outdir, exist_ok=True)
    for i, p in enumerate(prompts, 1):
        full = f"{p}，{args.style}"
        print(f"[{i}/{len(prompts)}] 生成中: {p[:40]}...")
        task = submit(full, size, key)
        url = poll(task, key)
        out = os.path.join(args.outdir, f"img-{i:02d}.png")
        with open(out, "wb") as f:
            f.write(requests.get(url, timeout=120).content)
        print(f"  -> {out}")

if __name__ == "__main__":
    main()
