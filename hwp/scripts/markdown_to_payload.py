#!/usr/bin/env python3
"""Convert structured Markdown into a payload JSON for report_writer.py."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
LIST_RE = re.compile(r"^(\d+\.\s+|[-*]\s+).+")
CODE_RE = re.compile(r"`([^`]*)`")


def strip_links(text: str) -> str:
    result: list[str] = []
    i = 0
    while i < len(text):
        if text[i] == "[":
            label_end = text.find("](", i)
            if label_end != -1:
                depth = 1
                j = label_end + 2
                while j < len(text) and depth > 0:
                    if text[j] == "(":
                        depth += 1
                    elif text[j] == ")":
                        depth -= 1
                    j += 1
                if depth == 0:
                    result.append(text[i + 1 : label_end])
                    i = j
                    continue
        result.append(text[i])
        i += 1
    return "".join(result)


def clean_text(text: str) -> str:
    text = strip_links(text)
    text = CODE_RE.sub(r"\1", text)
    text = text.replace("**", "")
    return " ".join(text.split())


def parse_table(lines: list[str], start: int) -> tuple[dict[str, object], int]:
    table_lines: list[str] = []
    i = start
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped.startswith("|"):
            break
        table_lines.append(stripped)
        i += 1

    rows = []
    for raw in table_lines:
        cells = [clean_text(cell.strip()) for cell in raw.strip("|").split("|")]
        rows.append(cells)

    if len(rows) < 2:
        raise ValueError("Markdown table must include a separator row")

    headers = rows[0]
    body = []
    for row in rows[2:]:
        if len(row) != len(headers):
            raise ValueError("Markdown table row length does not match header length")
        body.append(row)

    return {"headers": headers, "rows": body}, i


def flush_paragraph(paragraph_lines: list[str], section: dict[str, object]) -> None:
    if not paragraph_lines:
        return
    text = clean_text(" ".join(paragraph_lines))
    if text:
        section.setdefault("paragraphs", []).append(text)
    paragraph_lines.clear()


def flush_section(section: dict[str, object] | None, sections: list[dict[str, object]]) -> None:
    if not section:
        return
    if section.get("paragraphs") or section.get("table"):
        sections.append(section)


def new_section(title: str, subtitle: str | None) -> dict[str, object]:
    return {
        "title": clean_text(title),
        "subtitle": clean_text(subtitle or "주요 내용"),
        "paragraphs": [],
    }


def parse_markdown(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()

    title = path.stem
    date_label = ""
    sections: list[dict[str, object]] = []
    paragraph_lines: list[str] = []
    current_section: dict[str, object] | None = None
    headings: dict[int, str] = {}

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_paragraph(paragraph_lines, current_section or {})
            i += 1
            continue

        heading_match = HEADING_RE.match(stripped)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = clean_text(heading_match.group(2))

            if level == 1:
                title = heading_text
                i += 1
                continue

            if 2 <= level <= 4:
                flush_paragraph(paragraph_lines, current_section or {})
                flush_section(current_section, sections)
                headings = {k: v for k, v in headings.items() if k < level}
                headings[level] = heading_text
                parent_levels = [k for k in headings if k < level]
                parent_title = headings[max(parent_levels)] if parent_levels else "주요 내용"
                current_section = new_section(heading_text, parent_title)
                i += 1
                continue

        if current_section is None and stripped.startswith("(") and stripped.endswith(")"):
            date_label = clean_text(stripped)
            i += 1
            continue

        if stripped.startswith("|"):
            if current_section is None:
                current_section = new_section("표", "주요 내용")
            flush_paragraph(paragraph_lines, current_section)
            table, i = parse_table(lines, i)
            if current_section.get("table") is None:
                current_section["table"] = table
            else:
                flush_section(current_section, sections)
                current_section = new_section(f"{current_section['title']} 표", current_section["subtitle"])
                current_section["table"] = table
            continue

        if LIST_RE.match(stripped):
            if current_section is None:
                current_section = new_section("본문", "주요 내용")
            flush_paragraph(paragraph_lines, current_section)
            current_section.setdefault("paragraphs", []).append(clean_text(stripped))
            i += 1
            continue

        if current_section is None:
            current_section = new_section("본문", "주요 내용")
        paragraph_lines.append(stripped)
        i += 1

    flush_paragraph(paragraph_lines, current_section or {})
    flush_section(current_section, sections)

    payload = {
        "title": title,
        "date_label": date_label or "()",
        "sections": sections,
    }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert Markdown into an HWPX payload JSON.")
    parser.add_argument("--input", required=True, help="Source Markdown file.")
    parser.add_argument("--output", required=True, help="Destination JSON payload file.")
    parser.add_argument("--force", action="store_true", help="Overwrite the output file if it exists.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if output_path.exists() and not args.force:
        raise SystemExit(f"Output already exists: {output_path}")

    payload = parse_markdown(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote payload: {output_path.resolve()}")


if __name__ == "__main__":
    main()
