#!/usr/bin/env python3
"""生成金句出场音效（纯合成，无外部素材）— 上滑 whoosh + 双音 chime。

用法:
  python3 sfx.py --output assets/sfx_golden.wav
"""
import argparse, subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="assets/sfx_golden.wav")
    ap.add_argument("--duration", type=float, default=1.6)
    args = ap.parse_args()
    # 上滑噪声感 chirp + E5/A5 双音钟声，指数衰减，带回声空间感
    expr = ("0.30*sin(2*PI*(240+1500*t)*t)*exp(-4.5*t)"
            "+0.22*sin(2*PI*880*t)*exp(-5.5*t)"
            "+0.11*sin(2*PI*1318.51*t)*exp(-7*t)")
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        f"aevalsrc={expr}:s=48000:d={args.duration}",
        "-af", "aecho=0.7:0.6:60|110:0.25|0.12,loudnorm=I=-19:TP=-2:LRA=7",
        "-ar", "48000", "-ac", "1", args.output,
    ], check=True)
    print(f"OK {args.output}（{args.duration}s 金句音效）")


if __name__ == "__main__":
    main()
