# Revision Loop

## Purpose

Use this loop when the user reacts to a draft with qualitative feedback and wants the skill to improve over time.

## Routing

- One document only:
  Edit the payload or the source Markdown and regenerate.
- Same wording preference repeats:
  Update a rulebook JSON or a reference note.
- Same structural complaint repeats:
  Update the preset payload or markdown conversion logic.
- Generator behavior is wrong:
  Patch the Python script.

## Typical Feedback Mapping

- “검토목적은 항상 먼저 잡아줘”
  Add a required section or required phrase group in a rulebook. Update the preset if this is the default layout.
- “법정 기준이랑 관행을 분리해서 써줘”
  Add a required phrase group or a domain rule note. Validate future drafts against it.
- “이 표현은 너무 단정적이야”
  Add a forbidden phrase or weaker preferred language in a domain rule note.
- “표보다 문장 설명이 더 필요해”
  Update the preset structure and the generator usage guidance.

## Escalation Rule

If the user is manually fixing the same issue for the third time, stop treating it as ad hoc. Promote it into:

- `references/` when it is explanatory guidance
- `assets/rules/` when it is machine-checkable
- `scripts/` when the fix must be deterministic
