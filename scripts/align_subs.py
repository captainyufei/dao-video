#!/usr/bin/env python3
"""字幕时间轴对齐 — faster-whisper 只取时间点，文字用已确认的旁白。

原理：对最终旁白音频做词级转写（faster-whisper, language=zh,
compute_type=int8），把每个词的 (start, end) 按字符偏移拼接成一段
归一化文本；然后在其中按顺序查找每条旁白句子，得到每条句子的真实
起止时间。找不到的句子退回按字数比例估算，保证字幕永远不缺。

用法:
  python3 align_subs.py --audio assets/narration.wav \
    --sentences sentences.txt --output subs.json

输出:
  [{"start": 0.12, "end": 1.84, "text": "第一句……"}, ...]
"""
import argparse, json, re, unicodedata


def norm(s: str) -> str:
    """去掉标点/空白/大小写差异，只保留可用于对齐的字符。"""
    try:
        import zhconv
        s = zhconv.convert(s, "zh-cn")  # whisper 常输出繁体，统一转简体再匹配
    except ImportError:
        pass
    s = unicodedata.normalize("NFKC", s)
    s = s.lower()
    return re.sub(r"[\s\W_]+", "", s, flags=re.UNICODE)


def load_sentences(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if not lines:
        raise SystemExit(f"sentences 为空: {path}")
    return lines


SOFT_BREAK = set("的得地着了过是在就把让那这也都能会要钱人来书去里")


def split_chunks(text: str, max_chars: int = 12) -> list[str]:
    """把旁白拆成适合单行显示的字幕片段。

    1. 先按中文标点切；
    2. 超过 max_chars 的片段，优先在区间 [55%, 75%] 内的语气词/虚词后断；
    3. 实在没有合适断点就按 max_chars 硬切，保证每条 ≤ max_chars。
    """
    parts = re.split(r"[，。！？、；：,.;!?]", text)
    parts = [p.strip() for p in parts if p.strip()]
    chunks = []
    for part in parts:
        while len(part) > max_chars:
            lo = int(max_chars * 0.55)
            hi = max(lo, max_chars - 3)
            cut = -1
            for i in range(min(hi, len(part) - 1), lo - 1, -1):
                if part[i] in SOFT_BREAK:
                    cut = i + 1
                    break
            if cut < lo:
                cut = max_chars
            chunks.append(part[:cut])
            part = part[cut:]
        chunks.append(part)
    return chunks


def transcribe_words(audio: str):
    """惰性导入 faster-whisper，避免未安装时报错。返回 [(word, start, end)]。"""
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise SystemExit(
            "缺少 faster-whisper，请先安装：pip install faster-whisper"
        ) from e
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _info = model.transcribe(
        audio,
        language="zh",
        initial_prompt="以下是简体中文旁白。",
        word_timestamps=True,
        vad_filter=True,
    )
    words = []
    for seg in segments:
        for w in (seg.words or []):
            words.append((w.word, float(w.start), float(w.end)))
    return words


def fuzzy_find(transcript: str, target: str, cursor: int, max_subs: int = 2) -> int:
    """允许 whisper 认错 1-2 个字的模糊查找，返回绝对位置；找不到返回 -1。"""
    import itertools, re
    idxs = list(range(len(target)))
    for subs in range(1, max_subs + 1):
        for combo in itertools.combinations(idxs, subs):
            pat = list(target)
            for i in combo:
                pat[i] = "."
            m = re.search("".join(pat), transcript[cursor:])
            if m:
                return cursor + m.start()
    return -1


def align(sentences: list[str], words: list[tuple[str, float, float]]) -> list[dict]:
    """按顺序把句子匹配到词级时间轴。"""
    # 归一化后的全文字符串 + 每个字符对应的 (start, end)
    chars = []
    for word, start, end in words:
        for ch in norm(word):
            if ch:
                chars.append((ch, start, end))
    transcript = "".join(c[0] for c in chars)
    if not transcript:
        raise SystemExit("faster-whisper 没有转写出任何词，请检查音频或安装模型")

    subs, cursor, total = [], 0, sum(len(norm(s)) for s in sentences)
    fallback_count = 0
    for s in sentences:
        target = norm(s)
        if not target:
            continue
        pos = transcript.find(target, cursor)
        if pos == -1:
            pos = fuzzy_find(transcript, target, cursor)
        if pos == -1:
            # 个别句子识别不全：退回按字数比例估算（时间轴由前后句兜底）
            fallback_count += 1
            subs.append({"text": s, "start": None, "end": None, "fallback": True})
            continue
        start = chars[pos][1]
        end = chars[pos + len(target) - 1][2]
        subs.append({"text": s, "start": round(start, 3), "end": round(end, 3)})
        cursor = pos + len(target)

    # 给 fallback 句子补时间：按连续段落分摊，每段夹在最近的已匹配句之间
    i, n = 0, len(subs)
    while i < n:
        if not subs[i].get("fallback"):
            i += 1
            continue
        j = i
        while j < n and subs[j].get("fallback"):
            j += 1
        seg_start = subs[i - 1]["end"] if i > 0 else 0.0
        seg_end = subs[j]["start"] if j < n else float(chars[-1][2])
        span = max(0.0, seg_end - seg_start)
        fb_chars = [len(norm(subs[k]["text"])) for k in range(i, j)]
        fb_total = sum(fb_chars) or 1
        t = seg_start
        for k, cnt in zip(range(i, j), fb_chars):
            d = span * cnt / fb_total
            subs[k].update({"start": round(t, 3), "end": round(t + d, 3)})
            del subs[k]["fallback"]
            t += d
        i = j
    if fallback_count:
        print(f"⚠ 警告: {fallback_count}/{len(subs)} 条字幕未匹配到语音，已按字数比例估算，"
              f"请检查繁简/识别差异")
    return subs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True, help="最终旁白音频")
    ap.add_argument("--sentences", help="旁白句子，一行一句")
    ap.add_argument("--text", help="旁白全文（配合 --chunk 自动拆短字幕）")
    ap.add_argument("--chunk", action="store_true", help="自动拆短字幕")
    ap.add_argument("--max-chars", type=int, default=12, help="短字幕最大字数")
    ap.add_argument("--output", default="subs.json")
    args = ap.parse_args()

    if args.chunk:
        if not args.text:
            raise SystemExit("--chunk 需要 --text 旁白全文")
        text = open(args.text, encoding="utf-8").read().strip()
        sentences = split_chunks(text, args.max_chars)
        print(f"拆分为 {len(sentences)} 条短字幕（≤{args.max_chars} 字）")
    else:
        if not args.sentences:
            raise SystemExit("请提供 --sentences 或 --text --chunk")
        sentences = load_sentences(args.sentences)
    words = transcribe_words(args.audio)
    subs = align(sentences, words)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(subs, f, ensure_ascii=False, indent=1)
    print(f"OK 对齐完成 {len(subs)} 条字幕 -> {args.output}")
    for sub in subs:
        print(f"  [{sub['start']:>6.2f} -> {sub['end']:>6.2f}] {sub['text']}")


if __name__ == "__main__":
    main()
