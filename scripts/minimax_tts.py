#!/usr/bin/env python3
"""MiniMax 音色复刻 + 语音合成 — 用参考音频克隆音色后合成旁白
用法:
  克隆并合成: minimax_tts.py --ref-audio 参考.wav --voice-id my-voice --text 旁白.txt --output narration.wav
  仅合成(已有 voice-id): minimax_tts.py --voice-id my-voice --text 旁白.txt --output narration.wav
  语气控制:   --emotion calm|fluent|whisper|sad...  --speed 0.9  --pitch -0.3
  精确对齐:   --subtitle  （同时导出句级时间戳到 <output>.subtitle.json，供 make_srt.py --subtitle 使用）
文本标签(仅 speech-2.8-hd/turbo): <#0.3#>停顿秒数 / (breath)换气 / (sighs)叹气 / (inhale)(exhale)(emm)
需要: MINIMAX_API_KEY 环境变量（platform.minimaxi.com 获取）
"""
import argparse, json, os, subprocess, sys
import requests
from dao_config import get, load_config

BASE = "https://api.minimaxi.com"
SYNTH_SUBTITLE = False

def upload(key, path, purpose):
    with open(path, "rb") as f:
        r = requests.post(f"{BASE}/v1/files/upload",
            headers={"Authorization": f"Bearer {key}"},
            data={"purpose": purpose},
            files={"file": (os.path.basename(path), f)}, timeout=120)
    d = r.json()
    if r.status_code != 200:
        sys.exit(f"上传失败: {json.dumps(d, ensure_ascii=False)[:300]}")
    return d["file"]["file_id"]

def clone(key, file_id, voice_id, preview_text):
    r = requests.post(f"{BASE}/v1/voice_clone",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"file_id": file_id, "voice_id": voice_id,
              "text": preview_text, "model": "speech-2.8-hd"}, timeout=300)
    d = r.json()
    if r.status_code != 200:
        sys.exit(f"克隆失败: {json.dumps(d, ensure_ascii=False)[:300]}")
    print("✅ 音色克隆成功:", voice_id)
    return d

def synth(key, voice_id, text, out, emotion="", speed=1.0, pitch=0):
    voice_setting = {"voice_id": voice_id, "speed": speed, "vol": 1, "pitch": int(pitch)}
    if emotion:
        voice_setting["emotion"] = emotion
    req = {"model": "speech-2.8-hd", "text": text,
           "voice_setting": voice_setting,
           "audio_setting": {"format": "mp3", "sample_rate": 32000},
           "output_format": "url", "stream": False}
    if SYNTH_SUBTITLE:
        req["subtitle_enable"] = True
    r = requests.post(f"{BASE}/v1/t2a_v2",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=req, timeout=300)
    d = r.json()
    if r.status_code != 200 or not d.get("data"):
        sys.exit(f"TTS 失败: {r.status_code} {r.text[:300]}")
    url = d["data"]["audio"]
    open(out.replace(".wav", ".mp3"), "wb").write(requests.get(url, timeout=120).content)
    if SYNTH_SUBTITLE and d["data"].get("subtitle_file"):
        sub = requests.get(d["data"]["subtitle_file"], timeout=30).text
        sub_path = out.replace(".wav", ".subtitle.json")
        open(sub_path, "w", encoding="utf-8").write(sub)
        print("字幕时间戳已导出:", sub_path)
    subprocess.run(["ffmpeg", "-y", "-i", out.replace(".wav", ".mp3"),
                    "-ar", "48000", "-ac", "1", out], check=True, capture_output=True)
    dur = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "csv=p=0", out]).decode().strip()
    print(f"OK 合成完成: {out}（{dur}s）")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-audio", help="复刻参考音频（10s-5min）")
    ap.add_argument("--voice-id")
    ap.add_argument("--text", required=True)
    ap.add_argument("--output", default="narration.wav")
    ap.add_argument("--emotion", default="", help="calm/fluent/whisper/sad/happy/angry/...（空=auto）")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--pitch", type=float, default=0.0)
    ap.add_argument("--subtitle", action="store_true", help="导出句级时间戳(精确对齐字幕)")
    ap.add_argument("--config")
    args = ap.parse_args()
    cfg = load_config(args.config)
    voice_id = args.voice_id or get(cfg, "voice.voice_id", "")
    if not voice_id:
        ap.error("需要 --voice-id，或在配置中填写 voice.voice_id")
    global SYNTH_SUBTITLE
    SYNTH_SUBTITLE = args.subtitle
    key = os.environ.get("MINIMAX_API_KEY")
    if not key:
        sys.exit("错误: 需要 MINIMAX_API_KEY 环境变量")
    text = open(args.text, encoding="utf-8").read().strip()
    if args.ref_audio:
        fid = upload(key, args.ref_audio, "voice_clone")
        print("上传完成 file_id:", fid)
        clone(key, fid, voice_id, text[:60])
    emotion = args.emotion or get(cfg, "voice.emotion", "")
    speed = args.speed if args.speed != 1.0 else float(get(cfg, "voice.speed", 1.0))
    synth(key, voice_id, text, args.output, emotion, speed, args.pitch)

if __name__ == "__main__":
    main()
