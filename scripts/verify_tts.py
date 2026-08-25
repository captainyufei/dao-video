#!/usr/bin/env python3
"""朗读校验 — 把 TTS 旁白转写回文本，与文案逐字比对，找出读错/漏读/多读
用法: verify_tts.py 文案.txt 旁白.wav
说明: faster-whisper large-v3-turbo 转写 → 去标点 → 与文案比对 → 拼音校验。
      「拼音一致」= 发音正确（whisper 选字差异，可忽略）；
      「拼音不同/字数差」= TTS 真读错或漏读多读，需修正（改文案/加注音）。
"""
import re, sys
from faster_whisper import WhisperModel
from pypinyin import pinyin, Style

def all_readings(ch):
    """返回字符的全部读音集合（多音字全覆盖，无声调——whisper 声调不可靠）"""
    return set(pinyin(ch, heteronym=True, style=Style.NORMAL)[0])

def clean(s):
    return re.sub(r'[^\u4e00-\u9fff]', '', s)  # 只留汉字

def main():
    text = clean(open(sys.argv[1], encoding='utf-8').read())
    audio = sys.argv[2]
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(audio, language="zh")
    rec = clean("".join(s.text for s in segs))
    print(f"文案字数: {len(text)} | 转写字数: {len(rec)}")
    # 对齐比对（简化：同位置字符比较 + 报告差异）
    n = max(len(text), len(rec))
    diffs = []
    for i in range(min(len(text), len(rec))):
        if text[i] != rec[i]:
            diffs.append((i, text[i], rec[i]))
    # 长度差说明漏/多字
    if len(text) != len(rec):
        print(f"⚠️ 字数不一致：文案 {len(text)} vs 朗读 {len(rec)}（可能漏读/多读）")
        print(f"   文案末尾: …{text[-30:]}")
        print(f"   朗读末尾: …{rec[-30:]}")
    real_errors = []
    print(f"差异字符数: {len(diffs)}")
    shown = 0
    for i, a, b in diffs:
        pa, pb = all_readings(a), all_readings(b)
        same_pinyin = bool(pa & pb)  # 存在一致读音即视为发音正确
        tag = "发音相同(whisper选字差)" if same_pinyin else "❌ 真读错"
        if not same_pinyin:
            real_errors.append((i, a, b))
        if shown >= 15:
            print("  ... 更多省略")
            break
        ctx = text[max(0,i-4):i+5]
        print(f"  位置{i}: 文案「{a}」 vs 朗读「{b}」  {tag}  上下文: …{ctx}…")
        shown += 1
    same = sum(1 for i in range(min(len(text), len(rec))) if text[i] == rec[i])
    print(f"\n逐字一致率: {same}/{min(len(text), len(rec))} = {same/max(1,min(len(text),len(rec)))*100:.1f}%")
    if len(text) != len(rec):
        print("❌ 字数不一致：存在漏读/多读，需人工听确认")
    if real_errors:
        print(f"❌ 真读错 {len(real_errors)} 处: {real_errors}")
        print("   修正方式：文案中加注音标注（如 处理/(chu3)(li3)）或换词")
    else:
        print("✅ 发音全部正确（差异均为 whisper 转写选字不同，不影响字幕）")

if __name__ == "__main__":
    main()
