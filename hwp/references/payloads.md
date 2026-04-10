# Payload Guide

## Required top-level fields

- `title`: document title shown on the cover
- `date_label`: parenthetical date or department label shown under the title
- `sections`: ordered section list

## Section object

Each entry in `sections` must contain:

- `title`: section heading text
- `subtitle`: short supporting line below the heading

Each entry must also contain at least one of:

- `paragraphs`: list of body lines
- `bullets`: alternative list key accepted by the generator
- `table`: structured table block

## Table object

Use `table` only when the document needs a comparison or summary matrix.

- `headers`: required list of column labels
- `rows`: required 2D list of row values
- `widths`: optional relative width weights

Rules:

1. Every row must have the same number of cells as `headers`.
2. `widths` should have the same number of values as `headers` when provided.
3. `widths` are relative weights, not absolute HWP units.

## Preset selection

- `report`: progress, result, or status reports
- `review-draft`: single-target review or recommendation drafts
- `comparison-review-draft`: multi-option comparison and recommendation documents
- `example`: quick smoke-test payload

## Minimal example

```json
{
  "title": "문서 제목",
  "date_label": "(26.03.26 작성부서)",
  "sections": [
    {
      "title": "보고 개요",
      "subtitle": "배경 및 목적",
      "paragraphs": [
        "첫 번째 핵심 문장",
        "두 번째 핵심 문장"
      ]
    }
  ]
}
```

## Authoring rules

- Use UTF-8 JSON.
- Keep most documents within 4 to 7 sections for predictable fit.
- Prefer short, direct sentences over long wrapped paragraphs.
- Keep one idea per paragraph item.
- Legacy payloads may include `wrap_width`, but the current generator ignores that field.
