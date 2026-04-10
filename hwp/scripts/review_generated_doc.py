#!/usr/bin/env python3
"""Validate generated HWPX or payload JSON drafts against a simple rulebook."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


HP_NS = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}


def extract_hwpx_text(path: Path) -> str:
    with zipfile.ZipFile(path, "r") as zf:
        root = ET.fromstring(zf.read("Contents/section0.xml"))
    texts = [node.text for node in root.findall(".//hp:t", HP_NS) if node.text]
    return "\n".join(texts)


def extract_payload_text(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    lines = [str(payload.get("title", "")), str(payload.get("date_label", ""))]
    for section in payload.get("sections", []):
        lines.append(str(section.get("title", "")))
        lines.append(str(section.get("subtitle", "")))
        for key in ("paragraphs", "bullets", "post_paragraphs"):
            for item in section.get(key, []):
                lines.append(str(item))
        table = section.get("table")
        if table:
            lines.extend(str(value) for value in table.get("headers", []))
            for row in table.get("rows", []):
                lines.extend(str(value) for value in row)
    return "\n".join(lines)


def load_text(path: Path) -> str:
    if path.suffix.lower() == ".hwpx":
        return extract_hwpx_text(path)
    if path.suffix.lower() == ".json":
        return extract_payload_text(path)
    raise SystemExit(f"Unsupported document type: {path.suffix}")


def validate(text: str, rules: dict[str, object]) -> list[str]:
    failures: list[str] = []
    for phrase in rules.get("required_phrases", []):
        if str(phrase) not in text:
            failures.append(f"Missing required phrase: {phrase}")
    for phrase in rules.get("forbidden_phrases", []):
        if str(phrase) in text:
            failures.append(f"Found forbidden phrase: {phrase}")
    for item in rules.get("conditional_forbidden", []):
        phrase = str(item.get("phrase", ""))
        unless_any = [str(value) for value in item.get("unless_any", [])]
        if phrase and phrase in text and not any(exception in text for exception in unless_any):
            failures.append(f"Found conditionally forbidden phrase without exception: {phrase}")
    for group in rules.get("required_any", []):
        phrases = [str(item) for item in group.get("phrases", [])]
        if phrases and not any(phrase in text for phrase in phrases):
            failures.append(f"Missing one of group `{group.get('label', 'unnamed')}`: {phrases}")
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review a generated HWPX or payload JSON draft.")
    parser.add_argument("--document", required=True, help="HWPX or JSON payload to validate.")
    parser.add_argument("--rules", required=True, help="Rulebook JSON path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    document_path = Path(args.document)
    rules_path = Path(args.rules)
    text = load_text(document_path)
    rules = json.loads(rules_path.read_text(encoding="utf-8-sig"))
    failures = validate(text, rules)
    if failures:
        print("REVIEW FAILED")
        for failure in failures:
            print(f"- {failure}")
        sys.exit(1)
    print("REVIEW OK")


if __name__ == "__main__":
    main()
