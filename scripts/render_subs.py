#!/usr/bin/env python3
"""PIL 字幕渲染 — 把 SRT 渲染为透明 PNG（白字+半透明黑底条+柔阴影），输出 ffmpeg overlay 片段
用法: render_subs.py --srt subs.srt --outdir subpgs [--font /path/Xingkai.ttc] [--size 70]
输出: subpgs/sub-01.png... 与 subpgs/overlay.txt（可拼入 filter_complex）
特性: 强制单行（超宽自动缩字号至多 40px）、底部居中、55% 黑底条、6px 高斯模糊阴影
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--srt", required=True)
    ap.add_argument("--outdir", default="subpgs")
    ap.add_argument("--font", default="/System/Library/AssetsV2/com_apple_MobileAsset_Font8/13b8ce423f920875b28b551f9406bf1014e0a656.asset/AssetData/Xingkai.ttc")
    ap.add_argument("--size", type=int, default=70, help="字号(px)，超宽自动缩小")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--margin-v", type=int, default=90, help="底部边距(px)")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    lines = open(args.srt, encoding='utf-8').read().strip().split('\n')

    items, i = [], 0
    while i < len(lines):
        if lines[i].strip().isdigit():
            i += 1
            st_s, en_s = lines[i].replace(',', '.').split(' --> ')
            def to_sec(x):
                p = x.split(':')
                return str(round(int(p[0])*3600 + int(p[1])*60 + float(p[2]), 3))
            st, en = to_sec(st_s), to_sec(en_s)
            i += 1
            txt = []
            while i < len(lines) and lines[i].strip():
                txt.append(lines[i]); i += 1
            items.append((st, en, " ".join(txt)))
        i += 1

    pad_x, pad_y = 44, 24
    chain, inp = [], "[vc]"
    for k, (st, en, text) in enumerate(items, 1):
        # 强制单行：超宽自动缩字号（70 → 2px 递减，下限 40）
        cur_size = args.size
        while cur_size > 40:
            f = ImageFont.truetype(args.font, cur_size, index=1)
            tmp = Image.new("RGBA", (10, 10)); dd = ImageDraw.Draw(tmp)
            if dd.textlength(text, font=f) <= args.width - 160:
                break
            cur_size -= 2
        font = ImageFont.truetype(args.font, cur_size, index=1)
        # 精确文本包围盒（解决 glyph 基线偏移，保证底条内视觉居中）
        bb = dd.textbbox((0, 0), text, font=font, stroke_width=2)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        W, H = int(tw) + pad_x*2, int(th) + pad_y*2
        base_x, base_y = pad_x - bb[0], pad_y - bb[1]
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        # 阴影层（高斯模糊 6px 柔阴影）
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.text((base_x+3, base_y+3), text, font=font, fill=(0, 0, 0, 200),
                stroke_width=2, stroke_fill=(0, 0, 0, 200))
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        img = Image.alpha_composite(img, sh)
        # 半透明黑底条（55%）
        ImageDraw.Draw(img).rounded_rectangle([2, 2, W-4, H-4], radius=16, fill=(0, 0, 0, 140))
        # 白色正文
        d2 = ImageDraw.Draw(img)
        d2.text((base_x, base_y), text, font=font, fill=(255, 255, 255, 255),
                stroke_width=2, stroke_fill=(0, 0, 0, 160))
        path = os.path.join(args.outdir, f"sub-{k:02d}.png")
        img.save(path)
        x = (args.width - W) // 2; y = args.height - H - args.margin_v
        nxt = "[vout]" if k == len(items) else f"[o{k}]"
        chain.append(f"{inp}[{k}:v]overlay=x={x}:y={y}:enable='between(t,{st},{en})'{nxt}")
        inp = nxt
        print(f"  sub-{k:02d}.png {W}x{H} @({x},{y}) 字号{cur_size} 单行")
    open(os.path.join(args.outdir, "overlay.txt"), "w").write(";\n".join(chain))
    print(f"OK {len(items)} 张字幕 PNG -> {args.outdir}/；overlay 片段 -> {args.outdir}/overlay.txt")

if __name__ == "__main__":
    main()
