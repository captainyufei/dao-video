#!/usr/bin/env python3
"""把音效按时间点混入旁白轨（不改变语音时间轴，字幕不用重新对齐）。

用法:
  python3 add_sfx.py --audio assets/narration_final.wav \
    --sfx assets/sfx_golden.wav --at 17.42 --volume 0.5 \
    --output assets/narration_final_sfx.wav
"""
import argparse, subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True, help="旁白后期轨")
    ap.add_argument("--sfx", required=True, help="音效文件")
    ap.add_argument("--at", type=float, required=True, help="音效起点（秒）")
    ap.add_argument("--volume", type=float, default=0.5, help="音效音量")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    ms = int(args.at * 1000)
    fc = (f"[1:a]adelay={ms},volume={args.volume}[sfx];"
          "[0:a][sfx]amix=inputs=2:duration=first:normalize=0[a]")
    subprocess.run([
        "ffmpeg", "-y", "-i", args.audio, "-i", args.sfx,
        "-filter_complex", fc, "-map", "[a]", "-ar", "48000", "-ac", "1",
        args.output,
    ], check=True)
    print(f"OK {args.output}（音效 @ {args.at}s）")


if __name__ == "__main__":
    main()
