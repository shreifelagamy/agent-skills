# Formatting Rules

These are the rules Claude must follow when formatting meeting notes. The template in `assets/meeting-template.md` shows the structure — this file explains the logic.

## Section ordering

Always use this order:
1. Decisions
2. Action Items
3. Open Questions
4. Key Discussion Points

Never reorder these sections.

## Handling missing info

- **Missing attendees:** write `not specified`
- **Missing date:** write `not specified`
- **Missing action item owner:** write `Unassigned`
- **Missing deadline:** write `no deadline` or `date TBD`

## Empty sections

If a section has no content, **omit it entirely**. Don't write "None" or "N/A."

Exception: always keep the **Attendees** and **Date** lines, even if their values are "not specified."

## Action item format

Strict format:
`- [ ] [Owner] — [task] ([deadline])`

Rules:
- Use an em dash (—) between owner and task, not a hyphen
- One task per line — never combine multiple tasks
- Owner comes first, then task, then deadline in parentheses

## What to never do

- Never invent attendees, dates, or owners that weren't in the raw notes
- Never expand short notes into long paragraphs
- Never add commentary or opinions about the meeting
- Never reorder or rename the four sections

## Good vs bad action items

✅ Good:
- `- [ ] Sarah — Draft press release (by Friday Oct 25)`
- `- [ ] Unassigned — Decide on mobile feature scope (no deadline)`

❌ Bad:
- `- Sarah will do the press release` (no checkbox, wrong format)
- `- [ ] Press release` (no owner)
- `- [ ] Sarah - draft press release and talk to PR and check with Tom` (multiple tasks combined)
