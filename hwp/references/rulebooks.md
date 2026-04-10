# Rulebooks

## Goal

Use rulebooks to validate whether a generated draft satisfies stable expectations before the user opens HWP manually.

## File Location

Store reusable rulebooks in `assets/rules/`.

## Shape

```json
{
  "name": "rulebook-name",
  "required_phrases": ["A", "B"],
  "forbidden_phrases": ["C"],
  "conditional_forbidden": [
    {
      "phrase": "D",
      "unless_any": ["E", "F"]
    }
  ],
  "required_any": [
    {
      "label": "law-vs-practice distinction",
      "phrases": ["법정", "관행"]
    }
  ]
}
```

## Guidance

- Use `required_phrases` for exact statements that must appear.
- Use `forbidden_phrases` for wording that should not appear.
- Use `conditional_forbidden` when a phrase is wrong in most cases but acceptable inside an explicit rebuttal or qualified statement.
- Use `required_any` for conceptual checks where any one phrase from a set is enough.
- Keep rulebooks short and specific to a document family.
- If a rule is too nuanced for phrase checks, capture it in a reference note or a vault decision note instead.
