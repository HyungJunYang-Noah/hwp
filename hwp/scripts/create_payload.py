#!/usr/bin/env python3
"""Copy a bundled JSON preset into the user's workspace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PRESETS = {
    "example": "example_report.json",
    "report": "preset_report.json",
    "review-draft": "preset_review_draft.json",
    "comparison-review-draft": "preset_comparison_review_draft.json",
}


def asset_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "payloads"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copy a bundled HWPX report payload preset.")
    parser.add_argument("--preset", choices=sorted(PRESETS), required=True, help="Preset name to copy.")
    parser.add_argument("--output", required=True, help="Path for the copied JSON payload.")
    parser.add_argument("--title", help="Optional override for payload.title.")
    parser.add_argument("--date-label", help="Optional override for payload.date_label.")
    parser.add_argument("--force", action="store_true", help="Overwrite the output file if it exists.")
    return parser.parse_args()


def load_preset(name: str) -> dict[str, object]:
    source = asset_dir() / PRESETS[name]
    with source.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)

    if output_path.exists() and not args.force:
        raise SystemExit(f"Output already exists: {output_path}")

    payload = load_preset(args.preset)
    if args.title:
        payload["title"] = args.title
    if args.date_label:
        payload["date_label"] = args.date_label

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote preset payload: {output_path.resolve()}")


if __name__ == "__main__":
    main()
