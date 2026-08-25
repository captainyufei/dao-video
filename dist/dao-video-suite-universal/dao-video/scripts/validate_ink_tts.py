#!/usr/bin/env python3
"""Stop water-ink production unless speech exactly matches visible captions."""

import argparse
import json
import re
from pathlib import Path


SPLIT_RE = re.compile(r"[。！？；，、：…,.!?;:\n]+")
STRIP_RE = re.compile(r"[\s。！？；，、：…,.!?;:]+")


def read_phrases(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8").strip()
    return [STRIP_RE.sub("", part) for part in SPLIT_RE.split(text) if STRIP_RE.sub("", part)]


def read_subtitle_phrases(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit(f"FAIL: subtitle payload must be a JSON list: {path}")
    phrases: list[str] = []
    for item in payload:
        if not isinstance(item, dict):
            raise SystemExit(f"FAIL: invalid subtitle item in {path}")
        text = str(item.get("text", ""))
        phrases.extend(STRIP_RE.sub("", part) for part in SPLIT_RE.split(text) if STRIP_RE.sub("", part))
    return phrases


def assert_equal(label: str, actual: list[str], expected: list[str]) -> None:
    if actual == expected:
        return
    print(f"FAIL: {label} does not match visible main captions")
    print(f"expected ({len(expected)}): {expected}")
    print(f"actual   ({len(actual)}): {actual}")
    for index in range(max(len(expected), len(actual))):
        want = expected[index] if index < len(expected) else "<missing>"
        got = actual[index] if index < len(actual) else "<missing>"
        if want != got:
            print(f"first mismatch at phrase {index + 1}: expected={want!r}, actual={got!r}")
            break
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-captions", required=True, type=Path)
    parser.add_argument("--narration", required=True, type=Path)
    parser.add_argument("--subtitle", type=Path)
    args = parser.parse_args()

    expected = read_phrases(args.main_captions)
    if not expected:
        raise SystemExit("FAIL: main-caption list is empty")
    assert_equal("narration", read_phrases(args.narration), expected)
    if args.subtitle:
        assert_equal("TTS subtitle payload", read_subtitle_phrases(args.subtitle), expected)
    print(f"OK: ink narration matches {len(expected)} visible main captions exactly")


if __name__ == "__main__":
    main()
