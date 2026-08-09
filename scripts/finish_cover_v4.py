#!/usr/bin/env python3
"""完成 v4 双参考封面：保留 Seedream 合成底图，只叠加标题和真实印章。

标题坐标由当次底图构图确定后传入；印章位置通过红色留位连通域自动检测。
"""
import argparse
from PIL import Image, ImageDraw, ImageFont

MOON = (245, 243, 237, 255)
SHADOW = (5, 7, 9, 240)
FONTS = [
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/13b8ce423f920875b28b551f9406bf1014e0a656.asset/AssetData/Xingkai.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]


def font(size):
    for path in FONTS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    raise RuntimeError("找不到行楷/宋体字体")


def red_bbox(im):
    px = im.convert("RGB")
    mask = set()
    for y in range(px.height):
        for x in range(px.width):
            r, g, b = px.getpixel((x, y))
            if r >= 125 and r > g * 1.75 and r > b * 1.65 and g < 90:
                mask.add((x, y))
    components = []
    while mask:
        seed = mask.pop()
        stack = [seed]
        xs, ys = [seed[0]], [seed[1]]
        while stack:
            x, y = stack.pop()
            for p in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if p in mask:
                    mask.remove(p)
                    stack.append(p)
                    xs.append(p[0])
                    ys.append(p[1])
        if len(xs) >= 500:
            components.append((len(xs), (min(xs), min(ys), max(xs) + 1, max(ys) + 1)))
    if not components:
        raise RuntimeError("未检测到空白朱砂红印块")
    # 空白印块是最大的连续高饱和朱砂红区域。
    return max(components, key=lambda item: item[0])[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--seal", required=True)
    ap.add_argument("--width", type=int, required=True)
    ap.add_argument("--height", type=int, required=True)
    ap.add_argument("--title-x", type=int, required=True)
    ap.add_argument("--title-y", type=int, default=-1)
    ap.add_argument("--font-size", type=int, required=True)
    ap.add_argument("--gap", type=int, required=True)
    args = ap.parse_args()

    im = Image.open(args.input).convert("RGBA").resize((args.width, args.height), Image.LANCZOS)
    box = red_bbox(im)
    bw, bh = box[2] - box[0], box[3] - box[1]
    seal = Image.open(args.seal).convert("RGBA")
    scale = min(bw / seal.width, bh / seal.height)
    seal = seal.resize((round(seal.width * scale), round(seal.height * scale)), Image.LANCZOS)
    sx = box[0] + (bw - seal.width) // 2
    sy = box[1] + (bh - seal.height) // 2
    im.alpha_composite(seal, (sx, sy))

    f = font(args.font_size)
    block_h = len(args.title) * args.font_size + (len(args.title) - 1) * args.gap
    y = args.title_y if args.title_y >= 0 else (args.height - block_h) // 2
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for ch in args.title:
        draw.text((args.title_x + 8, y + 9), ch, font=f, fill=SHADOW, anchor="mm")
        draw.text((args.title_x, y), ch, font=f, fill=MOON, anchor="mm")
        y += args.font_size + args.gap
    Image.alpha_composite(im, layer).convert("RGB").save(args.output)


if __name__ == "__main__":
    main()
