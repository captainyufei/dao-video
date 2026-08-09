#!/usr/bin/env python3
"""青云观封面一键合成（v3 模板：透明边框 + 主图 + 印章 + 白字黑阴影标题）

用法:
  python3 make_cover.py \
    --main-v assets/cover-main-3x4.png \
    --main-h assets/cover-main-4x3.png \
    --title 立秋养气 --seal brand/brand-seal.png --outdir 04-封面

主图由 Seedream 从视频人物帧生成（无边框、无文字、无印章、纯画幅）。
脚本只会输出两张最终封面：
  - 04-封面/竖版封面.png（1080x1440）
  - 04-封面/横版封面.png（1440x1080）
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

MOON = (245, 243, 237, 255)
SHADOW = (5, 7, 9, 240)
DEFAULT_FRAME_V = os.environ.get("DAO_VIDEO_FRAME_VERTICAL", "")
XPATH_FONTS = [
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/13b8ce423f920875b28b551f9406bf1014e0a656.asset/AssetData/Xingkai.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]


def pick_font(size, want="Bold"):
    for path in XPATH_FONTS:
        for idx in range(4):
            try:
                f = ImageFont.truetype(path, size, index=idx)
                name = f.getname()
                if want in name[1] and ("SC" in name[0] or "Songti" in name[0]):
                    return f
            except Exception:
                break
    return ImageFont.truetype(XPATH_FONTS[0], size)


def build_horizontal_frame(frame_v, out_w=1440, out_h=1080):
    """从竖版透明边框用九宫格拼接 4:3 横版边框。"""
    src = Image.open(frame_v).convert("RGBA")
    W, H = src.size
    corner = 180
    canvas = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))

    # 四角保持原比例；只拉伸中间边带，避免断层、重叠和云纹变形。
    canvas.alpha_composite(src.crop((0, 0, corner, corner)), (0, 0))
    canvas.alpha_composite(src.crop((W - corner, 0, W, corner)), (out_w - corner, 0))
    canvas.alpha_composite(src.crop((0, H - corner, corner, H)), (0, out_h - corner))
    canvas.alpha_composite(
        src.crop((W - corner, H - corner, W, H)),
        (out_w - corner, out_h - corner),
    )

    top = src.crop((corner, 0, W - corner, corner)).resize(
        (out_w - 2 * corner, corner), Image.LANCZOS
    )
    bottom = src.crop((corner, H - corner, W - corner, H)).resize(
        (out_w - 2 * corner, corner), Image.LANCZOS
    )
    left = src.crop((0, corner, corner, H - corner)).resize(
        (corner, out_h - 2 * corner), Image.LANCZOS
    )
    right = src.crop((W - corner, corner, W, H - corner)).resize(
        (corner, out_h - 2 * corner), Image.LANCZOS
    )
    canvas.alpha_composite(top, (corner, 0))
    canvas.alpha_composite(bottom, (corner, out_h - corner))
    canvas.alpha_composite(left, (0, corner))
    canvas.alpha_composite(right, (out_w - corner, corner))
    return canvas


def add_title(im, title, char_h, gap, title_x):
    W, H = im.size
    font = pick_font(char_h)
    block_h = len(title) * char_h + (len(title) - 1) * gap
    title_y = (H - block_h) // 2
    tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tl)
    y = title_y
    for ch in title:
        td.text((title_x + 8, y + 9), ch, font=font, fill=SHADOW, anchor="mm")
        td.text((title_x, y), ch, font=font, fill=MOON, anchor="mm")
        y += char_h + gap
    return Image.alpha_composite(im, tl)


def compose(main_img, frame_img, seal_img, title, char_h, gap, title_x, seal_w, seal_margin, seal_top):
    W, H = frame_img.size
    im = main_img.copy()
    im.alpha_composite(frame_img)
    sw = seal_w
    sh = round(seal_img.height * sw / seal_img.width)
    seal = seal_img.resize((sw, sh), Image.LANCZOS)
    im.alpha_composite(seal, (W - sw - seal_margin, seal_top))
    with_title = add_title(im, title, char_h, gap, title_x)
    return im, with_title


def cover_crop(im, out_w, out_h, focus_x=0.5, focus_y=0.5):
    """等比放大后裁切，不拉伸人物；焦点坐标使横竖版保留同一人物。"""
    scale = max(out_w / im.width, out_h / im.height)
    rw, rh = round(im.width * scale), round(im.height * scale)
    resized = im.resize((rw, rh), Image.LANCZOS)
    cx = focus_x * rw
    cy = focus_y * rh
    left = max(0, min(round(cx - out_w / 2), rw - out_w))
    top = max(0, min(round(cy - out_h / 2), rh - out_h))
    return resized.crop((left, top, left + out_w, top + out_h))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", default="", help="兼容旧用法：横竖共用一张主图")
    ap.add_argument("--main-v", default="", help="Seedream 单独生成的 3:4 竖版纯主图")
    ap.add_argument("--main-h", default="", help="Seedream 单独生成的 4:3 横版纯主图")
    ap.add_argument("--title", required=True, help="竖排标题，如：立秋养气")
    ap.add_argument("--seal", required=True, help="青云观印章 PNG 路径")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--frame-v", default=DEFAULT_FRAME_V, help="竖版透明边框路径")
    ap.add_argument("--frame-h", default="", help="横版透明边框路径（缺省自动由竖版拼接）")
    ap.add_argument("--mirror", action="store_true", help="水平镜像同一原始帧（不生成新人物）")
    ap.add_argument("--focus-x", type=float, default=0.5, help="裁切焦点 X，0~1")
    ap.add_argument("--focus-y", type=float, default=0.5, help="裁切焦点 Y，0~1")
    ap.add_argument("--focus-x-v", type=float, default=None, help="竖版单独裁切焦点 X")
    ap.add_argument("--focus-x-h", type=float, default=None, help="横版单独裁切焦点 X")
    args = ap.parse_args()

    if not args.frame_v:
        ap.error("需要 --frame-v，或设置 DAO_VIDEO_FRAME_VERTICAL")

    main_v_path = args.main_v or args.main
    main_h_path = args.main_h or args.main
    if not main_v_path or not main_h_path:
        ap.error("必须同时提供 --main-v 和 --main-h（或使用旧参数 --main）")

    os.makedirs(args.outdir, exist_ok=True)
    main_v = Image.open(main_v_path).convert("RGBA")
    main_h = Image.open(main_h_path).convert("RGBA")
    if args.mirror:
        main_v = ImageOps.mirror(main_v)
        main_h = ImageOps.mirror(main_h)
    seal_img = Image.open(args.seal).convert("RGBA")
    frame_v = Image.open(args.frame_v).convert("RGBA")
    frame_h = Image.open(args.frame_h).convert("RGBA") if args.frame_h else build_horizontal_frame(args.frame_v)

    # 竖版 1080x1440
    focus_x_v = args.focus_x if args.focus_x_v is None else args.focus_x_v
    focus_x_h = args.focus_x if args.focus_x_h is None else args.focus_x_h
    m_v = cover_crop(main_v, 1080, 1440, focus_x_v, args.focus_y)
    _, with_t = compose(m_v, frame_v, seal_img, args.title, 136, 24, 172, 91, 55, 150)
    with_t.convert("RGB").save(os.path.join(args.outdir, "竖版封面.png"))

    # 横版 1440x1080
    m_h = cover_crop(main_h, 1440, 1080, focus_x_h, args.focus_y)
    _, with_t = compose(m_h, frame_h, seal_img, args.title, 118, 21, 230, 121, 73, 100)
    with_t.convert("RGB").save(os.path.join(args.outdir, "横版封面.png"))

    print("完成：04-封面/竖版封面.png + 04-封面/横版封面.png")


if __name__ == "__main__":
    main()
