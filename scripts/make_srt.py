#!/usr/bin/env python3
"""生成 SRT 字幕：优先用 MiniMax 句级时间戳（精确），无则按字数比例
用法:
  make_srt.py 文案.txt 旁白.wav [subs.srt]                       # 字数比例（无时间戳）
  make_srt.py 文案.txt 旁白.wav [subs.srt] --subtitle 旁白.subtitle.json  # MiniMax 精确对齐
  make_srt.py 文案.txt 旁白.wav [subs.srt] --whisper             # whisper 字符级时间戳对齐（任意 TTS 可用）
说明: 按所有中文标点细拆为短句（每条字幕一行）；有时间戳时句子边界毫秒级精确，
      句内短句按字数细分（误差<0.3s），避免停顿标签造成的累积偏差。
"""
import argparse, json, re, subprocess, sys

def ts(x):
    return f"{int(x//3600):02d}:{int(x%3600//60):02d}:{x%60:06.3f}".replace('.', ',')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text_file")
    ap.add_argument("audio")
    ap.add_argument("out", nargs="?", default="subs.srt")
    ap.add_argument("--subtitle", help="MiniMax 句级时间戳 JSON（minimax_tts.py --subtitle 导出）")
    ap.add_argument("--whisper", action="store_true", help="用 faster-whisper 字符级时间戳对齐（任意旁白音频可用）")
    args = ap.parse_args()

    text = open(args.text_file, encoding='utf-8').read().strip()
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'csv=p=0', args.audio]).decode().strip())
    # 按所有中文标点细拆（标点不进入字幕）
    sentences = [s.strip() for s in re.split(r'[。！？；，、：…]+', text) if s.strip()]

    if args.whisper:
        from faster_whisper import WhisperModel
        model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
        segs = list(model.transcribe(args.audio, language="zh")[0])
        # 段级时间戳 + 字数→时间线性插值（段边界精确，段内按字数，不受同音字影响）
        points = [(0, segs[0].start if segs else 0)]
        cum = 0
        for s in segs:
            cum += len(s.text.strip())
            points.append((cum, s.end))
        def interp(x):
            if x <= points[0][0]:
                return points[0][1]
            for i in range(1, len(points)):
                if x <= points[i][0]:
                    x0, y0 = points[i-1]; x1, y1 = points[i]
                    return y0 + (y1 - y0) * (x - x0) / max(x1 - x0, 1)
            return points[-1][1]
        srt, cum_s = [], 0
        for n, target in enumerate(sentences, 1):
            st_t = interp(cum_s)
            cum_s += len(target)
            en_t = interp(cum_s)
            srt.append(f"{n}\n{ts(st_t)} --> {ts(en_t)}\n{target}\n")
        open(args.out, 'w', encoding='utf-8').write('\n'.join(srt))
        print(f"OK {args.out}: {len(sentences)} 句（whisper 段级插值对齐）, 旁白 {dur:.1f}s")
    elif args.subtitle:
        anchors = json.load(open(args.subtitle, encoding="utf-8"))
        # MiniMax 锚点已经包含权威文本和精确起止时间。只拆分各锚点自己的文本，
        # 禁止用跨锚点模糊子串匹配；像“哪些话”这样的重复短语会同时命中相邻
        # 锚点，旧算法因此生成重叠字幕。
        entries = []
        previous_end = 0.0
        for anchor_no, anchor in enumerate(anchors, 1):
            a_begin = anchor["time_begin"] / 1000.0
            a_end = anchor["time_end"] / 1000.0
            if a_begin < previous_end - 0.001:
                raise RuntimeError(
                    f"MiniMax 锚点时间重叠: 第 {anchor_no} 段从 {a_begin:.3f}s 开始，"
                    f"上一段到 {previous_end:.3f}s"
                )
            if a_end <= a_begin:
                raise RuntimeError(f"MiniMax 锚点时长无效: 第 {anchor_no} 段")
            group = [s.strip() for s in re.split(
                r'[。！？；，、：…]+', anchor.get("text", "")
            ) if s.strip()]
            if not group:
                previous_end = a_end
                continue
            weights = [max(len(x), 1) for x in group]
            total_w = sum(weights)
            cur = a_begin
            for gs, w in zip(group, weights):
                t2 = cur + (a_end - a_begin) * w / total_w
                entries.append((cur, t2, gs))
                cur = t2
            previous_end = a_end
        for n in range(1, len(entries)):
            if entries[n][0] < entries[n-1][1] - 0.001:
                raise RuntimeError(
                    f"字幕时间重叠: 第 {n} 条结束 {entries[n-1][1]:.3f}s，"
                    f"第 {n+1} 条开始 {entries[n][0]:.3f}s"
                )
        srt = [
            f"{n}\n{ts(start)} --> {ts(end)}\n{text}\n"
            for n, (start, end, text) in enumerate(entries, 1)
        ]
        open(args.out, 'w', encoding='utf-8').write('\n'.join(srt))
        print(f"OK {args.out}: {len(srt)} 句（MiniMax 时间戳对齐）, 旁白 {dur:.1f}s")
    else:
        # 全局字数加权（无时间戳时的降级方案）
        weights = [max(len(s), 1) for s in sentences]
        total_w = sum(weights)
        srt, t = [], 0.0
        for i, (s, w) in enumerate(zip(sentences, weights), 1):
            seg = dur * w / total_w
            if i == len(sentences):
                seg = dur - t
            t2 = min(t + seg, dur)
            srt.append(f"{i}\n{ts(t)} --> {ts(t2)}\n{s}\n")
            t = t2
        open(args.out, 'w', encoding='utf-8').write('\n'.join(srt))
        print(f"OK {args.out}: {len(sentences)} 句（字数比例）, 旁白 {dur:.1f}s")

if __name__ == "__main__":
    main()
