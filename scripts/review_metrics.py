#!/usr/bin/env python3
"""Append a platform metrics checkpoint and produce a concise review file."""
from __future__ import annotations

import argparse
import json
import statistics
from datetime import datetime
from pathlib import Path


RATE_FIELDS = {
    "completion_rate", "retention_2s", "retention_5s", "like_rate",
    "comment_rate", "share_rate", "save_rate", "follow_conversion",
}
COUNT_FIELDS = {
    "impressions", "views", "likes", "comments", "shares", "saves",
    "profile_visits", "new_followers",
}
VALUE_FIELDS = RATE_FIELDS | COUNT_FIELDS | {"avg_watch_seconds"}


def parse_metric(raw: str) -> tuple[str, float]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError("指标格式必须是 name=value")
    name, value = raw.split("=", 1)
    if name not in VALUE_FIELDS:
        raise argparse.ArgumentTypeError(f"不支持的指标: {name}")
    try:
        number = float(value.rstrip("%"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"指标不是数字: {raw}") from exc
    if value.endswith("%"):
        number /= 100
    return name, number


def median_baseline(rows: list[dict], platform: str, checkpoint: int, episode: str, limit: int) -> dict:
    comparable = [
        row for row in rows
        if row.get("platform") == platform
        and row.get("checkpoint_hours") == checkpoint
        and row.get("episode") != episode
    ][-limit:]
    baseline: dict[str, float] = {}
    for field in VALUE_FIELDS:
        values = [row["metrics"][field] for row in comparable if field in row.get("metrics", {})]
        if values:
            baseline[field] = statistics.median(values)
    return {"sample_size": len(comparable), "metrics": baseline}


def fmt_value(name: str, value: float) -> str:
    if name in RATE_FIELDS or name.endswith("_rate") or name == "follow_conversion":
        return f"{value:.2%}"
    if name == "avg_watch_seconds":
        return f"{value:.2f}s"
    return f"{value:,.0f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--episode", required=True, help="稳定的期次标识，如 20260809-闲下来")
    parser.add_argument("--title", required=True)
    parser.add_argument("--platform", required=True, choices=["douyin", "wechat-channels"])
    parser.add_argument("--checkpoint-hours", required=True, type=int)
    parser.add_argument("--published-at", help="ISO 8601 发布时间")
    parser.add_argument("--observed-at", default=datetime.now().astimezone().isoformat(timespec="seconds"))
    parser.add_argument("--metric", action="append", default=[], type=parse_metric)
    parser.add_argument("--source-note", default="manual")
    parser.add_argument("--hypothesis", default="")
    parser.add_argument("--next-change", default="")
    parser.add_argument("--target-metric", default="")
    parser.add_argument("--baseline-episodes", type=int, default=5)
    args = parser.parse_args()

    metrics = dict(args.metric)
    views = metrics.get("views")
    if views and views > 0:
        for count_name, rate_name in (
            ("likes", "like_rate"), ("comments", "comment_rate"),
            ("shares", "share_rate"), ("saves", "save_rate"),
            ("new_followers", "follow_conversion"),
        ):
            if count_name in metrics:
                metrics[rate_name] = metrics[count_name] / views

    review_dir = Path(args.project_root).expanduser().resolve() / "06-复盘"
    review_dir.mkdir(parents=True, exist_ok=True)
    history_path = review_dir / "metrics.jsonl"
    rows = []
    if history_path.exists():
        for line in history_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))

    baseline = median_baseline(rows, args.platform, args.checkpoint_hours, args.episode, args.baseline_episodes)
    record = {
        "episode": args.episode,
        "title": args.title,
        "platform": args.platform,
        "checkpoint_hours": args.checkpoint_hours,
        "published_at": args.published_at,
        "observed_at": args.observed_at,
        "source_note": args.source_note,
        "metrics": metrics,
        "baseline": baseline,
        "hypothesis": args.hypothesis,
        "next_change": args.next_change,
        "target_metric": args.target_metric,
    }
    with history_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    lines = [
        f"# {args.title} · {args.platform} · {args.checkpoint_hours}h 复盘",
        "",
        f"- 观察时间：`{args.observed_at}`",
        f"- 数据来源：{args.source_note}",
        f"- 可比基线样本：{baseline['sample_size']} 条",
        "",
        "## 指标",
        "",
        "| 指标 | 当前 | 基线中位数 | 变化 |",
        "|---|---:|---:|---:|",
    ]
    for name in sorted(metrics):
        current = metrics[name]
        base = baseline["metrics"].get(name)
        change = (current - base) / base if base not in (None, 0) else None
        if change is not None:
            lines.append(
                f"| `{name}` | {fmt_value(name, current)} | "
                f"{fmt_value(name, base)} | {change:+.1%} |"
            )
        else:
            lines.append(f"| `{name}` | {fmt_value(name, current)} | — | — |")
    lines += [
        "",
        "## 判断",
        "",
        f"- 事实：填写本期相对基线的明确变化。",
        f"- 假设：{args.hypothesis or '待分析'}",
        f"- 下期单变量调整：{args.next_change or '待决定'}",
        f"- 目标指标：{args.target_metric or '待决定'}",
        "- 验证结论：待下一期相同检查点补充 `effective / neutral / harmful / inconclusive`。",
        "",
    ]
    safe_title = "".join(ch for ch in args.title if ch not in '/\\:*?\"<>|').strip() or "episode"
    report_path = review_dir / f"{args.episode}-{safe_title}-{args.checkpoint_hours}h-{args.platform}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"已追加数据: {history_path}")
    print(f"已生成复盘: {report_path}")


if __name__ == "__main__":
    main()
