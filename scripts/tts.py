#!/usr/bin/env python3
"""图书号配音 — edge-tts（微软神经网络语音，免费无 key）
用法: tts.py --text narration.txt --voice zh-CN-XiaoxiaoNeural --output assets/narration.wav
"""
import argparse, asyncio, os, subprocess, sys
import edge_tts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    ap.add_argument("--output", default="assets/narration.wav")
    args = ap.parse_args()
    text = open(args.text, encoding="utf-8").read().strip()
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    mp3 = args.output.replace(".wav", ".mp3")
    async def run():
        c = edge_tts.Communicate(text, args.voice)
        await c.save(mp3)
    asyncio.run(run())
    # 转 48k mono wav
    subprocess.run(["ffmpeg", "-y", "-i", mp3, "-ar", "48000", "-ac", "1", args.output],
                   check=True, capture_output=True)
    dur = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", args.output]).decode().strip()
    print(f"OK {args.output} 时长 {dur}s 音色 {args.voice}")

if __name__ == "__main__":
    main()
