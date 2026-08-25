#!/usr/bin/env python3
"""全 API 链路最终合成 — 多段动态视频 + xfade 转场 + 旁白对齐 + BGM(ducking) + 字幕 overlay
用法:
  make_final.py --clips video/clip-01.mp4,video/clip-02.mp4,video/clip-03.mp4,video/clip-04.mp4 \
      --narration assets/narration.wav --subs-dir subpgs --out final.mp4
  make_final.py ... --bgm bgm.mp3 --bgm-vol 0.12   # 加 BGM（旁白时自动压低）
  make_final.py ... --transition smoothup --trans-dur 0.5   # 换转场类型/时长
原则: 画面总长 = n×段长 - 转场×重叠 ≥ 旁白时长（先配音后定段长，尾部留白好对齐）
"""
import argparse, json, os, re, subprocess, sys

def probe_dur(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'csv=p=0', path]).decode().strip())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", required=True)
    ap.add_argument("--narration", required=True)
    ap.add_argument("--subs-dir", required=True, help="render_subs.py 输出目录(overlay.txt+sub-*.png)")
    ap.add_argument("--bgm")
    ap.add_argument("--bgm-vol", type=float, default=0.12, help="BGM 音量（相对旁白 1.0）")
    ap.add_argument("--no-env", action="store_true", help="丢弃片段自带环境音（只用旁白+BGM）")
    ap.add_argument("--no-duck", action="store_true", help="BGM 恒定音量，不做 ducking（默认做）")
    ap.add_argument("--brand", default="", help="右上角印章账号名（如 青云观），空=不加")
    ap.add_argument("--disclaimer", default="智慧思考 不涉及宗教 无不良引导")
    ap.add_argument("--transition", default="fade", help="xfade 转场类型: fade/slideup/circleopen/smoothup/wipeleft 等")
    ap.add_argument("--trans-dur", type=float, default=0.4)
    ap.add_argument("--out", default="final.mp4")
    args = ap.parse_args()

    clips = [c.strip() for c in args.clips.split(",") if c.strip()]
    n = len(clips)
    durs = [probe_dur(c) for c in clips]
    total = sum(durs) - args.trans_dur * (n - 1)
    voice_dur = probe_dur(args.narration)
    print(f"片段 {n} 段 总长 {total:.1f}s | 旁白 {voice_dur:.1f}s | 尾部留白 {total-voice_dur:.1f}s")
    if total < voice_dur:
        sys.exit(f"❌ 画面 {total:.1f}s < 旁白 {voice_dur:.1f}s，先加长片段（每段应 ≥ {voice_dur/n + args.trans_dur*(n-1)/n:.1f}s）")

    # 1) xfade 链
    off = durs[0] - args.trans_dur
    f = []
    for i, d in enumerate(durs):
        f.append(f"[{i}:v]scale=1920:1080,fps=24,setsar=1[v{i}]")
    prev = "v0"
    for k in range(1, n):
        f.append(f"[{prev}][v{k}]xfade=transition={args.transition}:duration={args.trans_dur}:offset={off:.3f}[x{k}]")
        prev = f"x{k}"
        off = off + durs[k] - args.trans_dur
    vout = prev

    # 2) 音频：环境音(可选) + 旁白 + BGM(ducking)
    if not args.no_env:
        f.append("".join(f"[{i}:a]aresample=48000,atrim=0:{total+1:.1f}[a{i}];" for i in range(n)))
        f.append("".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[env];")
        f.append(f"[env]volume=0.30[ambv];")
    # 旁白 pad 到视频总长，防止 -shortest 截短视频；
    # 有 BGM 时 asplit=2 复制一份给 sidechain 侧链（同一 label 双消费会吞音）
    if args.bgm and not args.no_duck:
        f.append(f"[{n}:a]aresample=48000,volume=1.0,apad=whole_dur={total:.1f},asplit=2[voicev][scv];")
    else:
        f.append(f"[{n}:a]aresample=48000,volume=1.0,apad=whole_dur={total:.1f}[voicev];")
    if args.bgm:
        # BGM 先 loudnorm(linear，零延迟) 归一化到 -20 LUFS，再乘 bgm_vol（0.3 ≈ 间隙 -30dB，说话时 ducking 再压）
        f.append(f"[{n+1}:a]atrim=0:{total+1:.1f},loudnorm=I=-20:TP=-1.5:LRA=11:linear=true,volume={args.bgm_vol}[bgmv];")
        if args.no_duck:
            # 恒定音量：直接混音，不随人声起伏
            if args.no_env:
                f.append("[voicev][bgmv]amix=inputs=2:duration=longest:normalize=0[am];")
            else:
                f.append("[ambv][voicev][bgmv]amix=inputs=3:duration=longest:normalize=0[am];")
        else:
            f.append("[bgmv][scv]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400:makeup=1.2[bgmduck];")
            if args.no_env:
                f.append("[bgmduck][voicev]amix=inputs=2:duration=longest:normalize=0[am];")
            else:
                f.append(f"[ambv][bgmduck][voicev]amix=inputs=3:duration=longest:normalize=0[am];")
    else:
        if args.no_env:
            f.append("[voicev]anull[am];")
        else:
            f.append(f"[ambv][voicev]amix=inputs=2:duration=longest:normalize=0[am];")

    # 3) 字幕 overlay（输入编号：视频 0..n-1，旁白 n，BGM n+1，PNG 从 n+2 起）
    ov_path = os.path.join(args.subs_dir, "overlay.txt")
    ov = open(ov_path, encoding="utf-8").read().strip()
    png_base = n + (2 if args.bgm else 1)
    # sub-k 的输入编号 = png_base + (k-1)，故 [k:v] → [k+png_base-1:v]
    ov_fixed = re.sub(r'\[(\d+):v\]', lambda m: f"[{int(m.group(1))+png_base-1}:v]", ov)
    ov_fixed = ov_fixed.replace("[vc]", f"[{vout}]")
    f.append(ov_fixed)
    # 最终视频输出 = overlay 链的最后一行输出 label（如 [vout]）
    last_line = [l for l in ov_fixed.split(";") if l.strip()][-1]
    m = re.findall(r'\[([A-Za-z0-9_]+)\]', last_line)
    final_v = f"[{m[-1]}]" if m else f"[{vout}]"

    import glob
    sub_pngs = sorted(glob.glob(os.path.join(args.subs_dir, "sub-*.png")))

    # 3.5) 品牌印章 + 免责声明（右上角/底部）
    brand_inputs = []
    if args.brand:
        import subprocess as sp
        os.makedirs("brand", exist_ok=True)
        sp.run(["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "seal_brand.py"),
                "--name", args.brand, "--outdir", "brand", "--disclaimer", args.disclaimer],
               check=True, capture_output=True)
        brand_inputs = ["brand/brand-seal.png", "brand/brand-disclaimer.png"]
        base_idx = n + (2 if args.bgm else 1) + len(sub_pngs)  # brand 输入起始编号
        prev_label = final_v
        from PIL import Image as PILImage
        seal_w, seal_h = PILImage.open(brand_inputs[0]).size
        disc_w, disc_h = PILImage.open(brand_inputs[1]).size
        # 角标：左 5%、顶 5%；声明：右 4%、顶 4%（单行横排）
        vw, vh = 1920, 1080
        sx, sy = int(vw * 0.05), int(vh * 0.05)
        dx = vw - disc_w - int(vw * 0.04)
        dy = int(vh * 0.04)
        fade_expr = f"fade=t=in:st=0:d=0.3,fade=t=out:st={max(total-0.3, 0.3):.2f}:d=0.3"
        f.append(f"[{base_idx}:v]{fade_expr}[bn1];")
        f.append(f"[{base_idx+1}:v]{fade_expr}[bn2];")
        f.append(f"{prev_label}[bn1]overlay=x={sx}:y={sy}[br1];")
        f.append(f"[br1][bn2]overlay=x={dx}:y={dy}[voutb]")
        final_v = "[voutb]"

    graph = ";\n".join(x.strip() for x in f if x.strip())
    while ";;" in graph:
        graph = graph.replace(";;", ";")
    open("filter-final.txt", "w", encoding="utf-8").write(graph + "\n")

    # 4) 组装命令
    cmd = ["ffmpeg", "-y"]
    for c in clips: cmd += ["-i", c]
    cmd += ["-i", args.narration]
    if args.bgm: cmd += ["-stream_loop", "-1", "-i", args.bgm]
    for p in sub_pngs:
        cmd += ["-loop", "1", "-t", f"{total+2:.0f}", "-i", p]
    for p in brand_inputs:
        cmd += ["-loop", "1", "-t", f"{total+2:.0f}", "-i", p]
    cmd += ["-filter_complex_script", "filter-final.txt", "-map", final_v, "-map", "[am]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", "-shortest", args.out]
    print("运行:", " ".join(cmd[:8]), "...")
    subprocess.run(cmd, check=True)
    print(f"✅ 成片: {args.out} ({total:.1f}s)")

if __name__ == "__main__":
    main()
