#!/usr/bin/env python3
"""方舟 Doubao 文案生成 — 走心模板（阿康配方）/ 节气模板（太虚观公式）
用法: ark_llm.py --topic "主题词" [--out 文案.txt] [--mode walkheart|jieqi]
需要: ARK API Key（arkcli auth login 后自动读取）
"""
import argparse, json, sys
import requests
from dao_config import ark_api_key, get, load_config

WALKHEART = """你是一位深谙道家智慧与现代心灵疗愈的作家。你的文字兼具哲思与温度，不引经据典，却处处暗合"道法自然"的内核。
请围绕用户给出的"主题词"，创作一段130字左右的走心文案（口播约30秒，对标抖音道家金句号）。

【风格核心要求】
1. 开头破题：用"从道家讲……"视角切入，语气平实，仿佛在轻声开解。
2. 核心痛点：点出常人对此事的"执念"或"后悔"，并用一个具体的迷茫意象（如"站在雾里"、"摸黑过河"、"逆风行走"）来描绘当年的自己。
3. 和解逻辑：必须包含"不能站在现在的高度批判当时的自己"或"以当时的阅历，依然会做同样的选择"这类逻辑，体现对过去的完全接纳。
4. 金句收尾：用一句带有诗意的比喻升华全篇（如水、棋局、种子、孤舟、月亮等），制造"落子无悔"般的记忆点。
5. 语言禁忌：避免说教，避免"你应该"，避免引经据典的学术腔。全是推心置腹的理解。

主题词：{topic}"""

JIEQI = """你是一位道家养气内容创作者（对标抖音"太虚观"节气视频，40秒口播，130字左右）。请围绕节气「{topic}」创作一段文案，严格按以下结构：

【结构】
1. 玄机钩子（1句）：点出该节气"气机转换"的独特之处（天地之气如何变化）；
2. 三件事清单（主体）：给出该节气顺应天时的三件具体事（作息/饮食/心境），每件一句话，可用"第一/第二/第三"或自然排比；
3. 金句收尾（1-2句）：点出"顺应天时、养气养心"的道理，最后以"愿你……"祝福收尾。

【语言要求】
- 平实口语，有"道系"味道但不故弄玄虚；数字/节气名写中文；
- 用排比或三连增强节奏；避免说教、避免"你应该"；
- 全文130字左右（口播约40秒）。

节气：{topic}"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True, help="主题词")
    ap.add_argument("--out", default="narration.txt")
    ap.add_argument("--mode", default="walkheart", choices=["walkheart", "jieqi"])
    ap.add_argument("--model")
    ap.add_argument("--config")
    args = ap.parse_args()
    cfg = load_config(args.config)
    key = ark_api_key()
    if not key:
        sys.exit("错误: 未找到 ARK_API_KEY 环境变量")
    model = args.model or get(cfg, "models.ark_llm", "doubao-1-5-pro-32k-250115")
    prompt = (WALKHEART if args.mode == "walkheart" else JIEQI).format(topic=args.topic)
    r = requests.post("https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model,
              "messages": [{"role": "user", "content": prompt}],
              "max_tokens": 800}, timeout=120)
    d = r.json()
    if r.status_code != 200:
        sys.exit(f"LLM 失败: {json.dumps(d, ensure_ascii=False)[:300]}")
    text = d["choices"][0]["message"]["content"].strip()
    open(args.out, "w", encoding="utf-8").write(text)
    print(f"OK 文案已生成: {args.out}（{len(text)} 字）\n{text[:200]}...")

if __name__ == "__main__":
    main()
