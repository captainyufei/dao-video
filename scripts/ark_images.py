#!/usr/bin/env python3
"""方舟 Seedream 生图 — 黑金国风插画（用户提供的风格配方）
用法: ark_images.py --prompts prompts.txt --outdir assets [--scene 远景|近景|围合]
prompts.txt 每行一个场景描述；支持行内场景标记「远景|描述」「近景|描述」「围合|描述」，
无标记的行使用 --scene 默认值（脚本自动拼黑金国风风格 + 人物尺寸规则）
"""
import argparse, json, os, sys, time
import requests
from dao_config import ark_api_key, get, load_config

STYLE = ("黑金国风插画，{scene_rule}整体为烫金工笔线描新中式国风，纯黑暗调底色，"
         "人物与景物为黑色实体剪影，仅用细腻鎏金细线勾勒轮廓，鎏金金属浮雕光泽，"
         "低光仙侠静谧氛围，高对比，空灵禅意意境；年轻俊美的东方道长男子，约二十岁出头，"
         "面容清秀，剑眉星目，少年感，束发金冠，黑金流云刺绣道袍，黑色完整剪影，"
         "五官清晰，清冷沉稳，鎏金飘带舒展。16:9，画面中没有任何文字")

SCENE_RULES = {
    "远景": "如果是宏大远景场景，人物只占画面高度25%到40%，放在画面边缘或下方局部区域，重点表现天地辽阔；",
    "近景": "如果是近景人物场景，人物占画面高度55%到75%，突出上半身和面部气质；",
    "围合": "如果是围合式小场景，人物居中，占画面高度45%到65%，四周景物环绕但不遮挡。",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--outdir", default="assets")
    ap.add_argument("--scene", default="围合", choices=["远景", "近景", "围合"])
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--model")
    ap.add_argument("--config")
    args = ap.parse_args()
    cfg = load_config(args.config)
    key = ark_api_key()
    if not key:
        sys.exit("错误: 未找到 ARK_API_KEY 环境变量")
    model = args.model or get(cfg, "models.seedream", "doubao-seedream-5-0-pro-260628")
    os.makedirs(args.outdir, exist_ok=True)
    prompts = [l.strip() for l in open(args.prompts, encoding="utf-8") if l.strip()]
    H = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    for i, p in enumerate(prompts, 1):
        scene = args.scene
        desc = p
        if "|" in p:
            tag, _, desc = p.partition("|")
            if tag.strip() in SCENE_RULES:
                scene = tag.strip()
        full = f"{desc}。{STYLE.format(scene_rule=SCENE_RULES[scene])}"
        print(f"[{i}/{len(prompts)}] 生图中: {p[:30]}...")
        r = requests.post("https://ark.cn-beijing.volces.com/api/v3/images/generations",
            headers=H, json={"model": model, "prompt": full,
                             "size": args.size, "watermark": False}, timeout=180)
        d = r.json()
        if r.status_code != 200:
            print(f"  ❌ {json.dumps(d, ensure_ascii=False)[:200]}"); continue
        url = d["data"][0]["url"]
        out = os.path.join(args.outdir, f"img-{i:02d}.png")
        open(out, "wb").write(requests.get(url, timeout=120).content)
        print(f"  -> {out}")

if __name__ == "__main__":
    main()
