---
name: meeting-notes-formatter
description: Turns raw meeting notes into a clean, structured summary with attendees, key decisions, action items, and next steps. Use when the user shares messy meeting notes, or asks to "format meeting notes", "clean up these notes", "write meeting minutes", "summarize the meeting", or pastes rough notes from a call.
---

# Meeting Notes Formatter

Take rough, unstructured meeting notes and turn them into a clean, shareable summary.

## Instructions

### Step 1: Read the raw notes
Identify the meeting's purpose, attendees, and rough date if mentioned.

### Step 2: Extract the four core elements
Pull out:
- **Decisions made** — what was agreed on
- **Action items** — who does what, by when
- **Open questions** — anything unresolved
- **Key discussion points** — context worth keeping

If any element is missing from the raw notes, leave the section empty rather than inventing content.

### Step 3: Apply the formatting rules
Before writing the output, consult `references/formatting-rules.md` for:
- Section ordering
- How to handle missing info
- Action item format
- What to do with edge cases

### Step 4: Fill in the template
Use the template at `assets/meeting-template.md` as the exact output structure. Replace the bracketed placeholders with content extracted from the notes.

### Step 5: Review before delivering
Check that:
- Every action item has an owner (or is flagged "Unassigned")
- No content was invented
- The summary is shorter than the raw notes

## Example

**User pastes:**
> "Met with Sarah and Tom about the launch. We decided to push to March 15. Sarah will handle the press release by next Friday. Tom needs to talk to legal — not sure when. Still debating whether to include the mobile feature in v1."

**Output:**

```
# Launch Planning Meeting

**Attendees:** Sarah, Tom
**Date:** not specified

## Decisions
- Launch date moved to March 15

## Action Items
- [ ] Sarah — Draft press release (by next Friday)
- [ ] Tom — Sync with legal (date TBD)

## Open Questions
- Should the mobile feature ship in v1?
```

## Common issues

**The notes are too vague to extract action items.**
Don't guess. Add a note: "No clear action items identified — consider following up with attendees."

**Multiple meetings in one block of text.**
Ask the user to confirm before splitting, or format each as a separate section.
