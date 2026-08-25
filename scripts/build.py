#!/usr/bin/env python3
"""从 config.json 生成 HyperFrames 图书号视频项目
config.json 字段:
  book, author, narration, sentences[], images[], scene_map (句子索引->图索引),
  orientation (landscape|portrait), outdir
"""
import argparse, json, os, shutil, subprocess

def build(cfg):
    orientation = cfg.get("orientation", "landscape")
    if orientation == "landscape":
        W, H, SUB_FS, SUB_BOTTOM, MARK_FS = 1920, 1080, 64, 220, 44
        TITLE_FS, GOLD_FS, END_FS = 112, 84, 92
    else:
        # 竖屏：无底大字幕 + 安全区（抖音底部 UI 遮挡区），底边抬到 360px
        W, H, SUB_FS, SUB_BOTTOM, MARK_FS = 720, 1280, 40, 360, 24
        TITLE_FS, GOLD_FS, END_FS = 56, 44, 48
    sentences = cfg["sentences"]
    images = cfg["images"]
    scene_map = cfg["scene_map"]  # [[0,1],[2,3],...] 每图对应句子索引范围
    out = cfg.get("outdir", "dao-video")
    src_assets = cfg.get("source_assets", "assets")
    audio_file = cfg.get("audio", "narration.wav")
    real_subs = cfg.get("subs")  # 可选: faster-whisper 对齐出的真实时间轴
    os.makedirs(os.path.join(out, "assets"), exist_ok=True)
    # 先复制素材，再探测音频时长
    for img in images:
        shutil.copy(os.path.join(src_assets, img.split("/")[-1]),
                    os.path.join(out, "assets", img.split("/")[-1]))
    shutil.copy(os.path.join(src_assets, audio_file),
                os.path.join(out, "assets", "narration.wav"))
    # 音频时长（用 ffprobe 实测，避免估算）
    nar = os.path.join(out, "assets", "narration.wav")
    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", nar]).decode().strip())
    if real_subs:
        # 真实时间轴：直接用 align_subs 输出的短字幕（含文本与时间）
        subs = []
        for i, rs in enumerate(real_subs):
            text = rs.get("text") or (sentences[i] if i < len(sentences) else "")
            start = rs.get("start", 0.0)
            end = rs.get("end", dur)
            if not (isinstance(start, (int, float)) and isinstance(end, (int, float))):
                start, end = 0.0, dur
            subs.append({"start": round(max(0.0, start), 2),
                         "end": round(min(dur, max(start, end)), 2), "text": text})
        # 兜底：任何一条缺时间则用相邻句补齐
        for i, sub in enumerate(subs):
            if sub["end"] <= sub["start"]:
                sub["end"] = round(dur, 2)
    else:
        chars = [len(s) for s in sentences]
        total = sum(chars) or 1
        subs = []
        t = 0.0
        for s, c in zip(sentences, chars):
            d = dur * c / total
            subs.append({"start": round(t, 2), "end": round(t + d, 2), "text": s})
            t += d
        subs[-1]["end"] = round(dur, 2)
    # ---- 模板卡：钩子标题 / 金句 / 结尾回响 ----
    import html as html_mod
    hook = cfg.get("hook")
    golden = cfg.get("golden") or {}
    ending = cfg.get("ending") or {}
    highlights = cfg.get("highlight", []) or []
    hook_start, hook_end = 0.0, cfg.get("hook_end", dur)
    golden_start, golden_end = golden.get("start"), golden.get("end")
    ending_start, ending_end = ending.get("start"), ending.get("end", dur)

    def overlaps(a, b, c, d):
        return not (b <= c or a >= d)

    display = []
    for s in subs:
        if hook and overlaps(s["start"], s["end"], hook_start, hook_end):
            continue
        if golden_start is not None and overlaps(s["start"], s["end"], golden_start, golden_end):
            continue
        if ending_start is not None and s["start"] >= ending_start:
            continue
        display.append(s)

    def fmt(text):
        t = html_mod.escape(text).replace("\n", "<br/>")
        for w in sorted(highlights, key=len, reverse=True):
            t = t.replace(w, f'<span class="hl">{w}</span>')
        return t

    scenes = []
    for gi, (s0, s1) in enumerate(scene_map):
        st = subs[s0]["start"] if s0 < len(subs) else 0
        if gi + 1 < len(scene_map):
            nxt = scene_map[gi + 1][0]
            en = subs[nxt]["start"] if nxt < len(subs) else dur
        else:
            en = dur
        en = max(en, st)
        scenes.append({"img": images[gi], "start": round(st, 2),
                       "end": round(en, 2), "dur": round(en - st, 2)})
    # 生成 index.html
    bg = "".join(
        f'<div id="bg{i}" class="bg clip" data-start="{s["start"]}" data-duration="{s["dur"]}">\n'
        f'  <img class="kenburns" style="animation-duration: {s["dur"]}s" src="assets/{s["img"]}" alt="" />\n</div>\n'
        for i, s in enumerate(scenes, 1))
    sub = "".join(
        f'<div id="s{i}" class="sub clip subfade" data-start="{s["start"]}" data-duration="{round(s["end"]-s["start"],2)}" '
        f'style="animation-duration: {round(s["end"]-s["start"],2)}s">{fmt(s["text"])}</div>\n'
        for i, s in enumerate(display, 1))
    cards = ""
    if hook:
        cards += (f'<div class="clip title-card" data-start="0" data-duration="{hook_end:.2f}">\n'
                  f'  <div class="card-scrim"></div>\n'
                  f'  <div class="card-body">\n'
                  f'    <div class="title-main">{fmt(hook)}</div>\n'
                  f'    <div class="title-sub">《{cfg["book"]}》 · {cfg.get("author","")}</div>\n'
                  f'  </div>\n</div>\n')
    if golden_start is not None:
        cards += (f'<div class="clip golden-card" data-start="{golden_start:.2f}" '
                  f'data-duration="{max(0.1, golden_end-golden_start):.2f}">\n'
                  f'  <div class="card-scrim"></div>\n'
                  f'  <div class="card-body">\n'
                  f'    <div class="golden-text">{fmt(golden["text"])}</div>\n'
                  f'    <div class="golden-src">——《{cfg["book"]}》</div>\n'
                  f'  </div>\n</div>\n')
    if ending_start is not None:
        cards += (f'<div class="clip end-card" data-start="{ending_start:.2f}" '
                  f'data-duration="{max(0.1, ending_end-ending_start):.2f}">\n'
                  f'  <div class="card-scrim"></div>\n'
                  f'  <div class="card-body">\n'
                  f'    <div class="end-text">{fmt(ending["text"])}</div>\n'
                  f'    <div class="end-book">《{cfg["book"]}》 · {cfg.get("author","")}</div>\n'
                  f'  </div>\n</div>\n')
    html = f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "PingFang SC"; src: local("PingFang SC"); }}
      @font-face {{ font-family: "Hiragino Sans GB"; src: local("Hiragino Sans GB"); }}
      @font-face {{ font-family: "Noto Sans CJK SC"; src: local("Noto Sans CJK SC"); }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      body {{ font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", sans-serif; }}
      .bg {{ position: absolute; inset: 0; }}
      .bg img {{ width: 100%; height: 100%; object-fit: cover; transform-origin: center center; }}
      .kenburns {{ animation-name: kb; animation-timing-function: linear; animation-fill-mode: both; }}
      @keyframes kb {{ from {{ transform: scale(1); }} to {{ transform: scale(1.06); }} }}
      .vignette {{ position: absolute; left: 0; right: 0; bottom: 0; height: 34%;
        background: linear-gradient(to top, rgba(0,0,0,.6), rgba(0,0,0,.25) 55%, transparent);
        pointer-events: none; }}
      .bookmark {{ position: absolute; top: 5%; right: 3%; text-align: right; color: rgba(255,255,255,.95);
        text-shadow: 0 2px 10px rgba(0,0,0,.6); letter-spacing: 1px;
        background: rgba(0,0,0,.45); border-radius: 12px; padding: 10px 18px; }}
      .bookmark .title {{ font-size: {MARK_FS}px; font-weight: 700; }}
      .bookmark .author {{ font-size: {int(MARK_FS*0.7)}px; font-weight: 400; opacity: .85; margin-top: 3px; }}
      .sub {{ position: absolute; left: 8%; right: 8%; bottom: {SUB_BOTTOM}px; color: #fff; text-align: center;
        font-size: {SUB_FS}px; font-weight: 800; line-height: 1.4; letter-spacing: 1px; white-space: nowrap;
        text-shadow: 0 0 10px rgba(0,0,0,.95), 0 3px 8px rgba(0,0,0,.9),
          3px 0 2px rgba(0,0,0,.85), -3px 0 2px rgba(0,0,0,.85),
          0 3px 2px rgba(0,0,0,.85), 0 -3px 2px rgba(0,0,0,.85); }}
      .sub .hl {{ color: #ffd76a; }}
      .subfade {{ animation-name: sf; animation-timing-function: ease; animation-fill-mode: both; }}
      @keyframes sf {{ 0% {{ opacity: 0; }} 4% {{ opacity: 1; }} 94% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
      .title-card, .golden-card, .end-card {{ position: absolute; inset: 0; color: #fff; }}
      .card-scrim {{ position: absolute; inset: 0;
        background: linear-gradient(180deg, rgba(0,0,0,.55), rgba(0,0,0,.25) 55%, rgba(0,0,0,.55)); }}
      .card-body {{ position: absolute; top: 34%; left: 6%; right: 6%; text-align: center; }}
      .title-main {{ font-size: {TITLE_FS}px; font-weight: 800; line-height: 1.4; letter-spacing: 2px;
        white-space: pre-line;
        text-shadow: 0 0 14px rgba(0,0,0,.95), 0 4px 10px rgba(0,0,0,.9); }}
      .title-sub {{ margin-top: 22px; font-size: {int(TITLE_FS*0.45)}px; font-weight: 600;
        color: #fff7df; letter-spacing: 4px; text-shadow: 0 2px 8px rgba(0,0,0,.9); }}
      .golden-text {{ font-size: {GOLD_FS}px; font-weight: 800; line-height: 1.6; letter-spacing: 2px;
        white-space: pre-line;
        text-shadow: 0 0 16px rgba(0,0,0,.95), 0 4px 12px rgba(0,0,0,.9); }}
      .golden-src {{ margin-top: 20px; font-size: {int(GOLD_FS*0.42)}px; color: #fff7df;
        letter-spacing: 3px; text-shadow: 0 2px 8px rgba(0,0,0,.9); }}
      .end-text {{ font-size: {END_FS}px; font-weight: 800; line-height: 1.5; letter-spacing: 2px;
        white-space: pre-line;
        text-shadow: 0 0 14px rgba(0,0,0,.95), 0 4px 10px rgba(0,0,0,.9); }}
      .end-book {{ margin-top: 18px; font-size: {int(END_FS*0.45)}px; color: #fff7df;
        letter-spacing: 3px; text-shadow: 0 2px 8px rgba(0,0,0,.9); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{round(dur,2)}"
         data-width="{W}" data-height="{H}">
{bg}
      <div class="vignette"></div>
      <div class="bookmark"><div class="title">《{cfg["book"]}》</div><div class="author">{cfg.get("author","")}</div></div>
{cards}
{sub}
      <audio id="vo" class="clip" data-start="0" data-duration="{round(dur,2)}" src="assets/narration.wav" preload="auto"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    timeline = {"duration": round(dur, 2), "subs": subs,
                "scenes": [{"image": s["img"], "start": s["start"], "end": s["end"]} for s in scenes]}
    with open(os.path.join(out, "timeline.json"), "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=1)
    print(f"OK 项目已生成: {out}/index.html（{round(dur,2)}s，{len(scenes)} 场景，{len(subs)} 字幕）")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config", help="config.json 路径")
    args = ap.parse_args()
    build(json.load(open(args.config, encoding="utf-8")))

if __name__ == "__main__":
    main()
