#!/usr/bin/env python3
"""旁白后期 + BGM ducking（FFmpeg）。

参数来自 369Serena 图书号流程实测：
- 旁白：volume=-2dB, highpass=70Hz, lowpass=13500Hz, acompressor,
  aecho 轻微空间感, loudnorm I=-16/TP=-1.5/LRA=8, 48k 重采样
- BGM：sidechaincompress（旁白说话时自动压低），可跳过前奏

用法:
  仅旁白后期:
    python3 post_audio.py --narration assets/narration.wav
  裁剪开头静音后再后期（推荐，保证字幕从 0 秒对齐）:
    python3 post_audio.py --narration assets/narration.wav --trim-silence
  旁白 + BGM ducking:
    python3 post_audio.py --narration assets/narration.wav \
      --bgm bgm.mp3 --bgm-start 19 --bgm-volume 0.16 \
      --output assets/mix.m4a
"""
import argparse, subprocess


NARR_FILTER = (
    "volume=-2dB,"
    "highpass=f=70,"
    "lowpass=f=13500,"
    "acompressor=threshold=-20dB:ratio=2.2:attack=18:release=180:makeup=1.5,"
    "aecho=0.7:0.14:34:0.06,"
    "loudnorm=I=-16:TP=-1.5:LRA=8,"
    "aresample=48000"
)

DUCK_FILTER = (
    "sidechaincompress=threshold=0.012:ratio=8:attack=45:release=650:makeup=1.4"
)


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--narration", required=True, help="原始旁白 wav")
    ap.add_argument("--bgm", help="BGM 文件（可选）")
    ap.add_argument("--bgm-start", type=float, default=0.0, help="BGM 从第几秒开始（跳过前奏）")
    ap.add_argument("--bgm-volume", type=float, default=0.16, help="BGM 基础音量")
    ap.add_argument("--trim-silence", action="store_true",
                    help="裁掉开头静音（silenceremove），让语音从 0 秒起")
    ap.add_argument("--output", default="assets/narration_final.wav", help="输出文件")
    args = ap.parse_args()

    # 1. 旁白后期
    proc = args.output
    if args.bgm:
        proc = args.output.replace(".wav", "_voice.wav").replace(".m4a", "_voice.wav")
    af = NARR_FILTER
    if args.trim_silence:
        af = ("silenceremove=start_periods=1:start_threshold=-45dB:"
              f"start_silence=0.1,{af}")
    run(["ffmpeg", "-y", "-i", args.narration, "-af", af,
         "-ar", "48000", "-ac", "1", proc])

    # 2. BGM ducking + 混音
    if args.bgm:
        out = args.output
        run(["ffmpeg", "-y", "-i", proc, "-i", args.bgm, "-filter_complex",
             f"[1:a]atrim=start={args.bgm_start},asetpts=PTS-STARTPTS,"
             f"volume={args.bgm_volume}[bg];"
             f"[bg][0:a]{DUCK_FILTER}[duckbg];"
             "[0:a][duckbg]amix=inputs=2:duration=first:dropout_transition=2,"
             "alimiter=limit=0.95[a]",
             "-map", "[a]", "-ar", "48000", "-ac", "2", out])
        print(f"OK 已输出带 BGM ducking 的混音: {out}")
    else:
        print(f"OK 旁白后期完成: {proc}")


if __name__ == "__main__":
    main()
