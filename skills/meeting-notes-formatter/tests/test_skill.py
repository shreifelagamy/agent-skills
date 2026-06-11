#!/usr/bin/env python3
"""
test_skill.py - A lightweight test harness for the meeting-notes-formatter skill.

It tests the three things every skill should be checked for:

  1. Triggering  - does the skill fire on the right requests, and stay quiet
                   on the wrong ones?
  2. Functional  - does the output follow the required structure and invent
                   nothing that wasn't in the notes?
  3. Consistency - does the same input produce the same SHAPE of output across
                   repeated runs?

The harness loads the REAL SKILL.md from the skill folder, so you are testing
the skill you actually ship - not a copy that drifts out of date.

------------------------------------------------------------------------------
Setup
------------------------------------------------------------------------------
  pip install requests
  export ANTHROPIC_API_KEY="sk-ant-..."
  # Optional: point at a model you have access to (default below).
  export ANTHROPIC_MODEL="claude-sonnet-4-5"

Run it:
  python test_skill.py --mode all
  python test_skill.py --mode trigger
  python test_skill.py --mode functional
  python test_skill.py --mode consistency --runs 5

------------------------------------------------------------------------------
How it works (and its honest limits)
------------------------------------------------------------------------------
A real agent decides whether to load a skill from its short DESCRIPTION. This
harness reproduces that decision by sending the description to the model as a
router prompt - so the trigger test really is testing your description text,
which is exactly the thing that makes skills fire or stay silent.

For functional and consistency tests, it feeds the full SKILL.md body to the
model as a system prompt and validates the output against the success criteria.

This is not the production Skills API - it is a fast, provider-style harness
you can run on every change. Swap call_model() for any provider you like.
"""

import argparse
import json
import os
import re
import sys
import urllib.request

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Path to the skill, relative to this file (tests/ lives inside the skill).
SKILL_DIR = os.path.join(os.path.dirname(__file__), "..")
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")

REQUIRED_SECTIONS = ["Attendees", "Decisions", "Action Items", "Open Questions"]

# --------------------------------------------------------------------------- #
# Test cases
# --------------------------------------------------------------------------- #
# Trigger cases: phrases that SHOULD fire the skill, and ones that should NOT.
TRIGGER_CASES = [
    # (query, should_trigger)
    ("Format these meeting notes for me", True),
    ("Can you clean up my notes from the call?", True),
    ("Write meeting minutes from this:", True),
    ("Summarize the meeting we just had", True),
    ("Met w/ Sarah and Tom, decided to ship March 15, Sarah does the PR...", True),
    ("What's the weather in San Francisco?", False),
    ("Help me write a Python function to sort a list", False),
    ("Create a spreadsheet of my expenses", False),
    ("Explain how OAuth works", False),
]

# Functional cases: messy input + facts we can check against the output.
FUNCTIONAL_CASES = [
    {
        "name": "happy_path_with_owners",
        "notes": (
            "Met with Sarah and Tom about the launch. We decided to push to "
            "March 15. Sarah will handle the press release by next Friday. "
            "Tom needs to talk to legal - not sure when. Still debating whether "
            "to include the mobile feature in v1."
        ),
        # No date is given, so the skill must NOT invent one.
        "must_not_contain_invented_date": True,
    },
    {
        "name": "vague_notes_no_clear_actions",
        "notes": (
            "Quick sync. Everyone agrees the homepage feels cluttered. "
            "We'll think about it more."
        ),
        "must_not_contain_invented_date": True,
    },
]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_skill():
    """Return (description, body) from the real SKILL.md."""
    if not os.path.exists(SKILL_MD):
        die(f"SKILL.md not found at {SKILL_MD}")
    text = open(SKILL_MD, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        die("SKILL.md is missing YAML frontmatter delimited by --- ... ---")
    frontmatter, body = m.group(1), m.group(2)
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE | re.DOTALL)
    if not desc_match:
        die("SKILL.md frontmatter has no 'description' field")
    description = desc_match.group(1).strip()
    return description, body


def call_model(system, user):
    """Minimal Anthropic Messages API call. Returns the text response."""
    if not API_KEY:
        die("Set ANTHROPIC_API_KEY in your environment first.")
    payload = {
        "model": MODEL,
        "max_tokens": 1024,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return "".join(b.get("text", "") for b in data.get("content", []))


def sections_present(output):
    """Return the set of required sections that appear as markdown headings."""
    found = set()
    for sec in REQUIRED_SECTIONS:
        if re.search(rf"^#+\s*{re.escape(sec)}", output, re.MULTILINE | re.IGNORECASE):
            found.add(sec)
    return found


# --------------------------------------------------------------------------- #
# Test 1: Triggering
# --------------------------------------------------------------------------- #
def test_triggering(description):
    print("\n=== 1. TRIGGERING ===")
    router_system = (
        "You are an agent's skill router. You decide whether a single skill "
        "should activate for a user message, based ONLY on the skill's "
        "description. Answer with exactly one word: YES or NO.\n\n"
        f"SKILL DESCRIPTION:\n{description}"
    )
    passed = 0
    for query, should in TRIGGER_CASES:
        answer = call_model(router_system, f'User message: "{query}"').strip().upper()
        fired = answer.startswith("YES")
        ok = fired == should
        passed += ok
        mark = "PASS" if ok else "FAIL"
        want = "trigger" if should else "stay quiet"
        print(f"  [{mark}] (expected: {want:11}) {query[:55]}")
    print(f"  -> {passed}/{len(TRIGGER_CASES)} trigger cases correct")
    return passed, len(TRIGGER_CASES)


# --------------------------------------------------------------------------- #
# Test 2: Functional
# --------------------------------------------------------------------------- #
def test_functional(body):
    print("\n=== 2. FUNCTIONAL ===")
    passed = 0
    total = 0
    for case in FUNCTIONAL_CASES:
        output = call_model(body, case["notes"])
        found = sections_present(output)
        checks = []

        # All required sections present.
        checks.append(("required sections present", found == set(REQUIRED_SECTIONS)))

        # Output should be shorter than the raw notes is not guaranteed for
        # tiny inputs, so we check it is not wildly longer instead.
        not_bloated = len(output.split()) <= len(case["notes"].split()) * 4
        checks.append(("output not bloated", not_bloated))

        # No invented date when the notes contain none.
        if case.get("must_not_contain_invented_date"):
            no_fake_date = bool(
                re.search(r"not specified|TBD|not mentioned|n/?a", output, re.IGNORECASE)
            ) or not re.search(r"\b\d{4}-\d{2}-\d{2}\b", output)
            checks.append(("no invented date", no_fake_date))

        for label, ok in checks:
            total += 1
            passed += ok
            print(f"  [{'PASS' if ok else 'FAIL'}] {case['name']}: {label}")
    print(f"  -> {passed}/{total} functional checks passed")
    return passed, total


# --------------------------------------------------------------------------- #
# Test 3: Consistency
# --------------------------------------------------------------------------- #
def test_consistency(body, runs):
    print(f"\n=== 3. CONSISTENCY ({runs} runs) ===")
    notes = FUNCTIONAL_CASES[0]["notes"]
    shapes = []
    for i in range(runs):
        output = call_model(body, notes)
        shape = tuple(sorted(sections_present(output)))
        shapes.append(shape)
        print(f"  run {i + 1}: sections = {list(shape)}")
    identical = len(set(shapes)) == 1
    print(f"  -> {'PASS' if identical else 'FAIL'}: "
          f"{'all runs produced the same structure' if identical else 'structure varied across runs'}")
    return (1 if identical else 0), 1


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(description="Test the meeting-notes-formatter skill.")
    parser.add_argument("--mode", choices=["trigger", "functional", "consistency", "all"],
                        default="all")
    parser.add_argument("--runs", type=int, default=5, help="runs for the consistency test")
    args = parser.parse_args()

    description, body = load_skill()
    print(f"Loaded skill. Model: {MODEL}")

    passed = total = 0
    if args.mode in ("trigger", "all"):
        p, t = test_triggering(description)
        passed += p; total += t
    if args.mode in ("functional", "all"):
        p, t = test_functional(body)
        passed += p; total += t
    if args.mode in ("consistency", "all"):
        p, t = test_consistency(body, args.runs)
        passed += p; total += t

    print("\n" + "=" * 50)
    print(f"TOTAL: {passed}/{total} checks passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
