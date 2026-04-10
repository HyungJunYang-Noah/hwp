#!/usr/bin/env python3
"""Generate a report-style HWPX document from a JSON payload."""

from __future__ import annotations

import argparse
import copy
import io
import json
from pathlib import Path
import re
import sys
import zipfile
import xml.etree.ElementTree as ET


HP_NS = "http://www.hancom.co.kr/hwpml/2011/paragraph"
HH_NS = "http://www.hancom.co.kr/hwpml/2011/head"
ET.register_namespace("hp", HP_NS)


def hp(tag: str) -> str:
    return f"{{{HP_NS}}}{tag}"


def hh(tag: str) -> str:
    return f"{{{HH_NS}}}{tag}"


def find_text_nodes(paragraph: ET.Element) -> list[ET.Element]:
    return paragraph.findall(f".//{hp('t')}")


def find_first(parent: ET.Element, path: str) -> ET.Element:
    found = parent.find(path)
    if found is None:
        raise RuntimeError(f"Missing expected node: {path}")
    return found


def strip_linesegarray(paragraph: ET.Element) -> None:
    for node in list(paragraph.findall(f"./{hp('linesegarray')}")):
        paragraph.remove(node)


def normalize_text(text: str) -> str:
    return " ".join(str(text).split())


def clear_run_children(run: ET.Element) -> None:
    for child in list(run):
        run.remove(child)


def keep_single_run(paragraph: ET.Element) -> ET.Element:
    runs = paragraph.findall(f"./{hp('run')}")
    if not runs:
        return ET.SubElement(paragraph, hp("run"))
    first = runs[0]
    for extra in runs[1:]:
        paragraph.remove(extra)
    clear_run_children(first)
    return first


def set_cover_title(paragraph: ET.Element, title: str) -> None:
    nodes = find_text_nodes(paragraph)
    if not nodes:
        return
    nodes[0].text = title
    for node in nodes[1:]:
        node.text = ""


def set_date_label(paragraph: ET.Element, date_label: str) -> None:
    nodes = find_text_nodes(paragraph)
    if nodes:
        nodes[0].text = date_label


def set_section_header(paragraph: ET.Element, number: int, title: str) -> None:
    nodes = find_text_nodes(paragraph)
    if len(nodes) >= 2:
        nodes[0].text = str(number)
        nodes[1].text = " " + title
    for node in nodes[2:]:
        node.text = ""


def set_subtitle(paragraph: ET.Element, subtitle: str) -> None:
    nodes = find_text_nodes(paragraph)
    if len(nodes) >= 2:
        nodes[1].text = " " + subtitle


def set_body(paragraph: ET.Element, content: str, bullet: bool = True) -> None:
    nodes = find_text_nodes(paragraph)
    if nodes:
        nodes[0].text = ("\uf06d " if bullet else "") + normalize_text(content)


def build_body_paragraph(body_template: ET.Element, text: str) -> ET.Element:
    paragraph = copy.deepcopy(body_template)
    strip_linesegarray(paragraph)
    set_body(paragraph, text, bullet=True)
    return paragraph


def build_plain_paragraph(body_template: ET.Element, text: str) -> ET.Element:
    paragraph = copy.deepcopy(body_template)
    strip_linesegarray(paragraph)
    set_body(paragraph, text, bullet=False)
    return paragraph


def is_note_text(text: str) -> bool:
    return re.match(r"^\s*주\s*\d+\)", str(text)) is not None


def build_body_or_plain_paragraph(body_template: ET.Element, text: str) -> ET.Element:
    if is_note_text(text):
        return build_plain_paragraph(body_template, text)
    return build_body_paragraph(body_template, text)


def build_styled_paragraph(
    template_para: ET.Element,
    text: str,
    *,
    para_pr_id: str | None = None,
    style_id: str | None = None,
    char_pr_id: str | None = None,
) -> ET.Element:
    paragraph = copy.deepcopy(template_para)
    strip_linesegarray(paragraph)

    if para_pr_id is not None:
        paragraph.set("paraPrIDRef", str(para_pr_id))
    if style_id is not None:
        paragraph.set("styleIDRef", str(style_id))

    run = keep_single_run(paragraph)
    if char_pr_id is not None:
        run.set("charPrIDRef", str(char_pr_id))
    text_node = ET.SubElement(run, hp("t"))
    text_node.text = normalize_text(text)
    return paragraph


def normalize_widths(count: int, width_weights: list[int] | None, total_width: int) -> list[int]:
    if width_weights and len(width_weights) == count and sum(width_weights) > 0:
        total_weight = sum(width_weights)
        widths = [int(total_width * weight / total_weight) for weight in width_weights]
    else:
        base = total_width // count
        widths = [base] * count
    widths[-1] += total_width - sum(widths)
    return widths


def load_style_info(header_xml: bytes) -> dict[str, dict[str, str]]:
    root = ET.fromstring(header_xml)
    styles_parent = find_first(root, f".//{hh('styles')}")
    result: dict[str, dict[str, str]] = {}
    for style in styles_parent.findall(f"./{hh('style')}"):
        name = style.attrib.get("name", "")
        result[name] = {
            "style_id": style.attrib.get("id", "0"),
            "para_pr_id": style.attrib.get("paraPrIDRef", "0"),
            "char_pr_id": style.attrib.get("charPrIDRef", "0"),
        }
    return result


def resolve_table_styles(style_map: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    center = style_map.get("표안글씨", {"style_id": "55", "para_pr_id": "30", "char_pr_id": "27"})
    left = style_map.get("(표)좌정렬", {"style_id": "56", "para_pr_id": "31", "char_pr_id": "28"})
    caption = style_map.get("9_표+그림제목", {"style_id": "57", "para_pr_id": "16", "char_pr_id": "29"})
    return {"center": center, "left": left, "caption": caption}


def build_cell_paragraph(
    template_para: ET.Element,
    text: str,
    *,
    para_pr_id: str,
    style_id: str,
    char_pr_id: str,
) -> ET.Element:
    return build_styled_paragraph(
        template_para,
        text,
        para_pr_id=para_pr_id,
        style_id=style_id,
        char_pr_id=char_pr_id,
    )


def resolve_cell_style(
    row_index: int,
    col_index: int,
    alignments: list[str] | None,
    table_styles: dict[str, dict[str, str]],
) -> dict[str, str]:
    if row_index == 0:
        return table_styles["center"]

    alignment = "left" if col_index == 0 else "center"
    if alignments and col_index < len(alignments):
        alignment = alignments[col_index]

    if alignment == "right":
        return {"style_id": "0", "para_pr_id": "37", "char_pr_id": "35"}
    if alignment == "center":
        return table_styles["center"]
    return table_styles["left"]


def build_table_block(
    table_para_template: ET.Element,
    table_cell_template: ET.Element,
    spec: dict[str, object],
    table_id: int,
    table_styles: dict[str, dict[str, str]],
) -> ET.Element:
    headers = [str(x) for x in spec["headers"]]
    rows = [[str(x) for x in row] for row in spec["rows"]]
    alignments = [str(x) for x in spec.get("alignments", [])] if spec.get("alignments") else None
    col_count = len(headers)
    if col_count == 0:
        raise ValueError("Table headers must not be empty")
    for row in rows:
        if len(row) != col_count:
            raise ValueError("Each table row must match header column count")

    table_para = copy.deepcopy(table_para_template)
    strip_linesegarray(table_para)
    run = keep_single_run(table_para)

    tbl = copy.deepcopy(find_first(table_para_template, f".//{hp('tbl')}"))
    clear_run_children(run)
    run.append(tbl)

    total_width = int(find_first(tbl, f"./{hp('sz')}").attrib["width"])
    widths = [int(x) for x in spec.get("widths", [])] if spec.get("widths") else None
    col_widths = normalize_widths(col_count, widths, total_width)

    tbl.attrib["id"] = str(table_id)
    tbl.attrib["rowCnt"] = str(len(rows) + 1)
    tbl.attrib["colCnt"] = str(col_count)
    tbl.attrib["borderFillIDRef"] = "17"
    for tr in list(tbl.findall(f"./{hp('tr')}")):
        tbl.remove(tr)

    row_heights: list[int] = []
    for row_index, row_values in enumerate([headers] + rows):
        tr = ET.SubElement(tbl, hp("tr"))
        row_height = 3000 if row_index == 0 else 2300
        row_heights.append(row_height)

        for col_index, value in enumerate(row_values):
            tc = ET.SubElement(
                tr,
                hp("tc"),
                {
                    "name": "",
                    "header": "0",
                    "hasMargin": "0",
                    "protect": "0",
                    "editable": "0",
                    "dirty": "0",
                    "borderFillIDRef": "17",
                },
            )
            sub_list = ET.SubElement(
                tc,
                hp("subList"),
                {
                    "id": "",
                    "textDirection": "HORIZONTAL",
                    "lineWrap": "BREAK",
                    "vertAlign": "CENTER",
                    "linkListIDRef": "0",
                    "linkListNextIDRef": "0",
                    "textWidth": "0",
                    "textHeight": "0",
                    "hasTextRef": "0",
                    "hasNumRef": "0",
                },
            )
            style = resolve_cell_style(row_index, col_index, alignments, table_styles)
            sub_list.append(
                build_cell_paragraph(
                    table_cell_template,
                    value,
                    para_pr_id=style["para_pr_id"],
                    style_id=style["style_id"],
                    char_pr_id=style["char_pr_id"],
                )
            )
            ET.SubElement(tc, hp("cellAddr"), {"colAddr": str(col_index), "rowAddr": str(row_index)})
            ET.SubElement(tc, hp("cellSpan"), {"colSpan": "1", "rowSpan": "1"})
            ET.SubElement(tc, hp("cellSz"), {"width": str(col_widths[col_index]), "height": str(row_height)})
            ET.SubElement(tc, hp("cellMargin"), {"left": "160", "right": "160", "top": "120", "bottom": "120"})

    find_first(tbl, f"./{hp('sz')}").attrib["height"] = str(sum(row_heights))
    return table_para


def build_placeholder_block(
    table_para_template: ET.Element,
    placeholder_para_template: ET.Element,
    table_id: int,
    table_styles: dict[str, dict[str, str]],
    height: int = 9000,
) -> ET.Element:
    table_para = copy.deepcopy(table_para_template)
    strip_linesegarray(table_para)
    run = keep_single_run(table_para)

    tbl = copy.deepcopy(find_first(table_para_template, f".//{hp('tbl')}"))
    clear_run_children(run)
    run.append(tbl)

    total_width = int(find_first(tbl, f"./{hp('sz')}").attrib["width"])
    tbl.attrib["id"] = str(table_id)
    tbl.attrib["rowCnt"] = "1"
    tbl.attrib["colCnt"] = "1"
    tbl.attrib["borderFillIDRef"] = "17"
    for tr in list(tbl.findall(f"./{hp('tr')}")):
        tbl.remove(tr)

    tr = ET.SubElement(tbl, hp("tr"))
    tc = ET.SubElement(
        tr,
        hp("tc"),
        {
            "name": "",
            "header": "0",
            "hasMargin": "0",
            "protect": "0",
            "editable": "0",
            "dirty": "0",
            "borderFillIDRef": "17",
        },
    )
    sub_list = ET.SubElement(
        tc,
        hp("subList"),
        {
            "id": "",
            "textDirection": "HORIZONTAL",
            "lineWrap": "BREAK",
            "vertAlign": "CENTER",
            "linkListIDRef": "0",
            "linkListNextIDRef": "0",
            "textWidth": "0",
            "textHeight": "0",
            "hasTextRef": "0",
            "hasNumRef": "0",
        },
    )
    center_style = table_styles["center"]
    sub_list.append(
        build_cell_paragraph(
            placeholder_para_template,
            "",
            para_pr_id=center_style["para_pr_id"],
            style_id=center_style["style_id"],
            char_pr_id=center_style["char_pr_id"],
        )
    )
    ET.SubElement(tc, hp("cellAddr"), {"colAddr": "0", "rowAddr": "0"})
    ET.SubElement(tc, hp("cellSpan"), {"colSpan": "1", "rowSpan": "1"})
    ET.SubElement(tc, hp("cellSz"), {"width": str(total_width), "height": str(height)})
    ET.SubElement(tc, hp("cellMargin"), {"left": "160", "right": "160", "top": "120", "bottom": "120"})

    find_first(tbl, f"./{hp('sz')}").attrib["height"] = str(height)
    return table_para


def build_caption_paragraph(
    body_template: ET.Element,
    text: str,
    caption_style: dict[str, str],
) -> ET.Element:
    return build_styled_paragraph(
        body_template,
        f"〈{text}〉",
        para_pr_id=caption_style["para_pr_id"],
        style_id=caption_style["style_id"],
        char_pr_id=caption_style["char_pr_id"],
    )


def build_section_blocks(
    header_template: ET.Element,
    subtitle_template: ET.Element,
    body_template: ET.Element,
    table_para_template: ET.Element,
    table_cell_template: ET.Element,
    sections: list[dict[str, object]],
    table_styles: dict[str, dict[str, str]],
) -> list[ET.Element]:
    blocks: list[ET.Element] = []
    next_table_id = 3100000000

    for idx, section in enumerate(sections, start=1):
        header = copy.deepcopy(header_template)
        subtitle = copy.deepcopy(subtitle_template)

        set_section_header(header, idx, str(section["title"]))
        set_subtitle(subtitle, str(section["subtitle"]))
        blocks.extend([header, subtitle])

        text_blocks = section.get("paragraphs", section.get("bullets", []))
        for text_block in text_blocks:
            blocks.append(build_body_or_plain_paragraph(body_template, str(text_block)))

        for placeholder in section.get("placeholders", []):
            if isinstance(placeholder, dict):
                label = str(placeholder.get("label", "자료 삽입"))
                height = int(placeholder.get("height", 9000))
            else:
                label = str(placeholder)
                height = 9000
            blocks.append(build_caption_paragraph(body_template, label, table_styles["caption"]))
            blocks.append(
                build_placeholder_block(
                    table_para_template,
                    table_cell_template,
                    next_table_id,
                    table_styles,
                    height,
                )
            )
            next_table_id += 1

        if section.get("table"):
            blocks.append(
                build_table_block(
                    table_para_template,
                    table_cell_template,
                    dict(section["table"]),
                    next_table_id,
                    table_styles,
                )
            )
            next_table_id += 1

        for text_block in section.get("post_paragraphs", []):
            blocks.append(build_body_or_plain_paragraph(body_template, str(text_block)))

        if idx != len(sections):
            blocks.append(build_plain_paragraph(body_template, ""))

    return blocks


def load_payload(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if "title" not in payload or "date_label" not in payload or "sections" not in payload:
        raise ValueError("Payload must include title, date_label, and sections")
    if not isinstance(payload["sections"], list) or not payload["sections"]:
        raise ValueError("sections must be a non-empty list")

    for section in payload["sections"]:
        if not isinstance(section, dict):
            raise ValueError("Each section must be an object")
        if "title" not in section or "subtitle" not in section:
            raise ValueError("Each section requires title and subtitle")

        bullets = section.get("bullets", [])
        paragraphs = section.get("paragraphs", [])
        post_paragraphs = section.get("post_paragraphs", [])
        placeholders = section.get("placeholders", [])
        table = section.get("table")

        if bullets and not isinstance(bullets, list):
            raise ValueError("bullets must be a list when provided")
        if paragraphs and not isinstance(paragraphs, list):
            raise ValueError("paragraphs must be a list when provided")
        if post_paragraphs and not isinstance(post_paragraphs, list):
            raise ValueError("post_paragraphs must be a list when provided")
        if placeholders and not isinstance(placeholders, list):
            raise ValueError("placeholders must be a list when provided")
        if not bullets and not paragraphs and not table and not post_paragraphs and not placeholders:
            raise ValueError("Each section must include paragraphs, bullets, post_paragraphs, placeholders, or a table")
        if table and ("headers" not in table or "rows" not in table):
            raise ValueError("table requires headers and rows")

    return payload


def write_hwpx(template_path: Path, output_path: Path, section0_xml: bytes) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(template_path, "r") as src, zipfile.ZipFile(
        output_path, "w", compression=zipfile.ZIP_DEFLATED
    ) as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename == "Contents/section0.xml":
                data = section0_xml
            dst.writestr(info, data)


def preserve_root_wrapper(original_xml: bytes, new_root: ET.Element) -> bytes:
    original_text = original_xml.decode("utf-8")
    xml_decl = ""
    body = original_text
    if original_text.startswith("<?xml"):
        decl_end = original_text.find("?>")
        if decl_end == -1:
            raise RuntimeError("Invalid XML declaration in section0.xml")
        xml_decl = original_text[: decl_end + 2]
        body = original_text[decl_end + 2 :]

    open_end = body.find(">")
    close_start = body.rfind("</")
    if open_end == -1 or close_start == -1:
        raise RuntimeError("Unexpected section0.xml structure")

    root_open = body[: open_end + 1]
    root_close = body[close_start:]

    serialized = ET.tostring(new_root, encoding="unicode")
    new_open_end = serialized.find(">")
    new_close_start = serialized.rfind("</")
    if new_open_end == -1 or new_close_start == -1:
        raise RuntimeError("Failed to serialize updated section root")

    inner_xml = serialized[new_open_end + 1 : new_close_start]
    return (xml_decl + root_open + inner_xml + root_close).encode("utf-8")


def build_document(template_path: Path, payload_path: Path, output_path: Path) -> None:
    payload = load_payload(payload_path)
    with zipfile.ZipFile(template_path, "r") as zf:
        section0 = zf.read("Contents/section0.xml")
        header_xml = zf.read("Contents/header.xml")

    root = ET.fromstring(section0)
    paragraphs = list(root)
    if len(paragraphs) < 7:
        raise RuntimeError("Unexpected template structure")

    style_map = load_style_info(header_xml)
    table_styles = resolve_table_styles(style_map)

    cover_template = copy.deepcopy(paragraphs[0])
    date_template = copy.deepcopy(paragraphs[1])
    section_header_template = copy.deepcopy(paragraphs[2])
    subtitle_template = copy.deepcopy(paragraphs[3])
    body_template = copy.deepcopy(paragraphs[4])
    table_para_template = copy.deepcopy(paragraphs[2])
    table_cell_template = copy.deepcopy(find_first(paragraphs[2], f".//{hp('tc')}[2]//{hp('p')}"))
    set_cover_title(cover_template, str(payload["title"]))
    set_date_label(date_template, str(payload["date_label"]))

    new_root = ET.Element(root.tag, root.attrib)
    new_root.append(cover_template)
    new_root.append(date_template)

    for block in build_section_blocks(
        section_header_template,
        subtitle_template,
        body_template,
        table_para_template,
        table_cell_template,
        payload["sections"],
        table_styles,
    ):
        new_root.append(block)

    section0_bytes = preserve_root_wrapper(section0, new_root)
    write_hwpx(template_path, output_path, section0_bytes)


def parse_args() -> argparse.Namespace:
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        base_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(description="Generate an HWPX report from a JSON payload.")
    parser.add_argument(
        "--template",
        default=str(base_dir / "templates" / "base_report_template.hwpx"),
        help="Template HWPX file path.",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Input JSON payload path.",
    )
    parser.add_argument(
        "--output",
        default=str(base_dir / "output" / "generated_report.hwpx"),
        help="Output HWPX path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_document(Path(args.template), Path(args.config), Path(args.output))
    print(f"Generated: {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
