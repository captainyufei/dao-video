#!/usr/bin/env python3
"""图书号配音 — VoxCPM2 本地 TTS（无 API，支持音色克隆）

用法:
  默认音色（Voice Design，自然语言描述声音）:
    python3 voxcpm_tts.py --text narration.txt --output assets/narration.wav
  可控克隆（参考音频 + 可选风格指令）:
    python3 voxcpm_tts.py --text narration.txt \
      --ref-audio 参考音频.wav --output assets/narration.wav

参数（369Serena 流程实测）:
  --cfg-value 2.0         条件跟随强度，自然感与稳定性平衡
  --inference-timesteps 10  正式版步数（快速测试用 8）
"""
import argparse, os, subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True, help="旁白文本文件")
    ap.add_argument("--ref-audio", help="参考音频路径（可控克隆音色）")
    ap.add_argument("--cfg-value", type=float, default=2.0)
    ap.add_argument("--inference-timesteps", type=int, default=10)
    ap.add_argument("--output", default="assets/narration.wav")
    ap.add_argument("--device", default="auto", help="auto/cpu/mps/cuda")
    ap.add_argument("--optimize", action="store_true", help="开启 torch.compile（MPS 上如报错请关闭）")
    args = ap.parse_args()

    text = open(args.text, encoding="utf-8").read().strip()
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    from voxcpm import VoxCPM
    import soundfile as sf

    print("加载 VoxCPM2（首次运行会自动下载权重）...")
    model = VoxCPM.from_pretrained(
        "openbmb/VoxCPM2",
        load_denoiser=False,
        device=args.device,
        optimize=args.optimize,
    )
    kw = {
        "cfg_value": args.cfg_value,
        "inference_timesteps": args.inference_timesteps,
    }
    if args.ref_audio:
        kw["reference_wav_path"] = args.ref_audio
    print(f"生成中（{args.inference_timesteps} 步，cfg={args.cfg_value}）...")
    wav = model.generate(text=text, **kw)

    tmp = args.output + ".raw.wav"
    sf.write(tmp, wav, model.tts_model.sample_rate)
    subprocess.run(["ffmpeg", "-y", "-i", tmp, "-ar", "48000", "-ac", "1",
                    args.output], check=True, capture_output=True)
    os.remove(tmp)
    dur = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", args.output]).decode().strip()
    print(f"OK {args.output} 时长 {dur}s VoxCPM2 cfg={args.cfg_value} steps={args.inference_timesteps}")


if __name__ == "__main__":
    main()
