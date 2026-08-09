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
        # 短句归属锚点：从当前锚点开始找，包含该短句的锚点
        srt, ai = [], 0
        def find_anchor(s, start):
            for k in range(start, len(anchors)):
                if s in anchors[k]["text"] or anchors[k]["text"] in s:
                    return k
            return None
        i = 0
        while i < len(sentences):
            k = find_anchor(sentences[i], ai)
            if k is None:
                # 兜底：剩余短句按余下时长均分
                k = len(anchors) - 1
            ai = max(ai, k)
            a_begin = anchors[k]["time_begin"] / 1000.0
            a_end = anchors[k]["time_end"] / 1000.0
            # 收集属于该锚点的连续短句
            group = [sentences[i]]
            j = i + 1
            while j < len(sentences):
                if find_anchor(sentences[j], k + 1) is not None:
                    break
                group.append(sentences[j]); j += 1
            # 句内按字数细分
            weights = [max(len(x), 1) for x in group]
            total_w = sum(weights)
            cur = a_begin
            for gs, w in zip(group, weights):
                t2 = cur + (a_end - a_begin) * w / total_w
                srt.append(f"{len(srt)+1}\n{ts(cur)} --> {ts(t2)}\n{gs}\n")
                cur = t2
            i = j
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
