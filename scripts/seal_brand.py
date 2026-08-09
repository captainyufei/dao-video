#!/usr/bin/env python3
"""国风品牌包装生成 — 左上角竖版朱砂角标（红底白字）+ 右上角常驻声明
用法: seal_brand.py --name 青云观 --outdir brand [--disclaimer "智慧思考｜传统文化分享｜不涉及宗教引导"]
输出: brand/brand-seal.png     (左上角角标, 红朱砂不规则底 + 白字竖排, 高≈画面22%)
      brand/brand-disclaimer.png (右上角声明, 白字+阴影, 单行)
"""
import argparse, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_XINGKAI = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/13b8ce423f920875b28b551f9406bf1014e0a656.asset/AssetData/Xingkai.ttc"

def make_seal(name, target_h=238, seed=23):
    """不规则朱砂印章底 + 白色竖排书法字（青/云/观 从上到下）"""
    random.seed(seed)
    scale = 4  # 4x 超采样，缩小后边缘更细腻
    H = target_h * scale
    W = int(H * 0.55)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # 朱砂红底：多块随机圆角矩形/椭圆叠加 → 毛笔刷痕、边缘不规则
    ink = (178, 34, 34, 255)
    m = int(W * 0.18)
    for _ in range(9):
        rx0 = random.randint(-int(W*0.15), int(W*0.15))
        ry0 = random.randint(-int(H*0.12), int(H*0.12))
        rw = random.randint(int(W*0.45), W - 2*m)
        rh = random.randint(int(H*0.2), H - 2*m)
        x0 = m + rx0; y0 = m + ry0
        x1 = min(W - m + rx0, W - 2); y1 = min(H - m + ry0, H - 2)
        if x1 <= x0 or y1 <= y0: continue
        style = random.choice(["round", "ellipse"])
        if style == "round":
            draw.rounded_rectangle([x0, y0, x1, y1], radius=random.randint(8, W//4), fill=ink)
        else:
            draw.ellipse([x0, y0, x1, y1], fill=ink)
    # 边缘柔和（印泥晕染）
    img = img.filter(ImageFilter.GaussianBlur(2.5))
    # 做旧：随机挖空（斑驳）
    px = img.load()
    for _ in range(int(W * H * 0.06)):
        x, y = random.randint(0, W-1), random.randint(0, H-1)
        r, g, b, a = px[x, y]
        if a > 0:
            px[x, y] = (r, g, b, max(0, a - random.randint(100, 220)))
    # 白色竖排书法字（青 云 观）
    font = ImageFont.truetype(FONT_XINGKAI, int(W * 0.42), index=1)
    d2 = ImageDraw.Draw(img)
    y = int(H * 0.06)
    step = int(H * 0.30)
    for ch in name:
        bb = d2.textbbox((0, 0), ch, font=font)
        cw = bb[2] - bb[0]
        cx = (W - cw) // 2 - bb[0]
        d2.text((cx, y - bb[1]), ch, font=font, fill=(255, 255, 255, 250))
        y += step
    # 缩小到目标尺寸
    img = img.resize((int(W/scale), target_h), Image.LANCZOS)
    return img

def make_disclaimer(text, size=30, seed=11):
    """右上角声明：白色书法字 + 黑阴影，透明底单行"""
    random.seed(seed)
    font = ImageFont.truetype(FONT_XINGKAI, size, index=1)
    tmp = Image.new("RGBA", (10, 10)); dd = ImageDraw.Draw(tmp)
    tw = dd.textlength(text, font=font)
    pad = 16
    W = int(tw) + pad * 2
    H = int(size * 1.7)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = (H - size) // 2
    d.text((pad + 2, y + 2), text, font=font, fill=(0, 0, 0, 220))
    d.text((pad, y), text, font=font, fill=(255, 255, 255, 235))
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--outdir", default="brand")
    ap.add_argument("--disclaimer", default="智慧思考｜传统文化分享｜不涉及宗教引导")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    seal = make_seal(args.name)
    seal.save(os.path.join(args.outdir, "brand-seal.png"))
    disc = make_disclaimer(args.disclaimer)
    disc.save(os.path.join(args.outdir, "brand-disclaimer.png"))
    print(f"OK: seal={seal.size} disclaimer={disc.size}")

if __name__ == "__main__":
    main()
