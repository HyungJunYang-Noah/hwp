---
name: hwp
description: Draft, revise, and validate Korean Hancom `.hwp` and `.hwpx` documents from sample templates, structured payloads, and bundled examples. Use when Codex needs to create or refine report-style Hancom documents such as 검토서, 요청서, 개략공사비 검토안, or other Korean forms; match an existing sample 양식; turn Markdown or notes into `.hwpx`; or use a task-provided legacy `.hwp` file as reference while producing a new `.hwpx` output.
---

# HWP

Use sample-first generation for Hancom documents. Prefer `.hwpx` for editable output and treat `.hwp` as reference material unless the user explicitly asks for a separate conversion or desktop-editing workflow.

This skill is bundled around a Korean `검토서` template family.

- Default generation template: `scripts/templates/base_report_template.hwpx`
- Source family: `검토서_기본템플릿.hwpx`
- Blank sample form: `examples/Sample.hwpx`, copied from `검토서_기본템플릿_빈양식.hwpx`

The generator preserves the packaged template structure, including the familiar boxed section layout, paragraph style IDs, and character styling from the Hancom source template instead of rebuilding the page from scratch.

## Default Workflow

1. Identify the closest document family.
   - Read `references/workspace-samples.md`.
   - Pick the nearest template or completed sample before drafting.
2. Build the structured payload.
   - Use `scripts/create_payload.py` when a bundled preset is close.
   - Use `scripts/markdown_to_payload.py` when the source already exists as Markdown.
   - Edit the payload JSON directly for one-off wording changes.
   - Replace bracketed placeholder text before expecting rulebook validation to pass.
3. Generate the draft.
   - Use `scripts/report_writer.py`.
   - Override `--template` when a different bundled sample is a better match.
4. Validate the draft when quality matters.
   - Use `scripts/review_generated_doc.py` with a rulebook from `assets/rules/`.
5. Promote repeated feedback into reusable behavior.
   - Update the payload for a one-off change.
   - Update a rulebook or reference note for repeated guidance.
   - Patch a script only when generator behavior is wrong.
6. Write outputs into the active task workspace, not into the skill folder.

## Commands

```powershell
python scripts/create_payload.py --preset review-draft --output .\payload.json --title "문서 제목"
python scripts/markdown_to_payload.py --input .\source.md --output .\payload.json
python scripts/report_writer.py --config .\payload.json --output .\result.hwpx
python scripts/report_writer.py --template .\assets\samples\blank_review_template.hwpx --config .\payload.json --output .\result.hwpx
python scripts/review_generated_doc.py --document .\result.hwpx --rules .\assets\rules\default-review-rulebook.json
```

## Format Boundaries

- Use `.hwpx` as the primary editable and generated format.
- Use `.hwp` samples as visual and structural references unless they are converted externally.
- Avoid hand-editing package XML unless the template structure or generator behavior must change.
- Treat a sample with a clearly different section skeleton as a new family instead of forcing the current preset to fit it.

## References

- Read `examples/` first when the user wants to mimic the bundled review-document family or asks for a concrete example.
- Read `references/workspace-samples.md` for the bundled template set and representative sample outputs.
- Read `references/payloads.md` for the payload schema and preset guidance.
- Read `references/revision-loop.md` when the user gives qualitative feedback on repeated drafts.
- Read `references/rulebooks.md` before adding or tightening machine-checkable validation.
- Read `references/domain-rules-urban-survey.md` for the land-development review defaults bundled with this skill.
- Read `references/document-family-model.md` when generalizing behavior from multiple example documents.

## Rules

1. Start from the closest sample or template, not from raw XML.
2. Prefer payload, rulebook, and template-choice changes over ad hoc document surgery.
3. Use task-provided `.hwp` files as references unless the user explicitly asks for a conversion workflow.
4. Keep generated outputs outside the skill folder.
5. When the same correction appears for the third time, promote it into reusable skill knowledge.
