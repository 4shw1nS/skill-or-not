# Worked examples

Seven cases in the output format. They cover the shapes most often confused:
composition, enforcement, packaging, the null verdict, and a genuine close call.

## Contents

- [1. Deterministic work, fuzzy invocation](#1-deterministic-work-fuzzy-invocation)
- [2. Prior art wins](#2-prior-art-wins)
- [3. Enforcement, not instruction](#3-enforcement-not-instruction)
- [4. Reach plus knowledge](#4-reach-plus-knowledge)
- [5. Judgment meets an unattended trigger](#5-judgment-meets-an-unattended-trigger)
- [6. A genuine close call](#6-a-genuine-close-call)
- [7. Audit of an existing skill](#7-audit-of-an-existing-skill)

---

## 1. Deterministic work, fuzzy invocation

> "I keep merging two images side by side for social posts. Same treatment every time."

| Axis | Answer |
|---|---|
| Judgment | Only which image goes left, and resolving vague file references |
| Trigger | A person, in conversation |
| Context | Main thread |
| Reach | Local files |
| Distribution | Public repo |

```
Build:        CLI script (Pillow, argparse)
Plus:         A near-empty skill for intent mapping — which image is left,
              resolving "the screenshot I just took" to a path
Don't build:  A skill body documenting the flags. That duplicates --help and
              will drift the first time you add one
Because:      Against — every step is closed-form once the two paths are known
Confidence:   High
Flips if:     The treatment starts varying by content (detecting faces, picking
              a canvas from subject matter). Then judgment moves into the loop
```

The composition is the answer. Neither shape alone is right.

---

## 2. Prior art wins

> "Convert HEIC photos to JPG."

Step 0 ends this: `sips -s format jpeg` ships with macOS; ImageMagick does it
anywhere.

```
Build:        Nothing
Plus:         A shell function if you type it often
Don't build:  A skill. Its description would occupy the system prompt in every
              session forever, in exchange for no judgment at all
Because:      Against — prior art
Confidence:   High
Flips if:     You need a specific pipeline around it (EXIF rules, naming
              conventions, a target directory structure). Then it's a script
```

---

## 3. Enforcement, not instruction

> "Stop Claude from ever running `rm -rf` on my machine."

```
Build:        A PreToolUse hook that blocks the pattern
Plus:         Deny rules in permission settings
Don't build:  A skill saying "never run rm -rf". A skill is a suggestion the
              model may not follow; a safety requirement needs a wall
Because:      Against — enforcement must be unbypassable
Confidence:   High
Flips if:     Nothing. Safety requirements never reduce to instructions
```

---

## 4. Reach plus knowledge

> "Let Claude query our warehouse, and always exclude test accounts."

Two problems wearing one coat. Claude can't reach the warehouse, *and* wouldn't
know the conventions if it could.

```
Build:        MCP server for warehouse access
Plus:         The conventions in the carrier G3 picks: standing facts with no
              steps — canonical tables, the test-account filter — go in
              CLAUDE.md; they move to a skill only once they grow steps
Don't build:  Either one alone, or a skill by reflex. A skill can't grant
              access; MCP can't know your filtering rules; and facts without
              steps don't need a skill to carry them
Because:      For — authenticated external reach, reusable across many tasks
Confidence:   High
Flips if:     Only one query ever matters. Then a script holding the
              credential beats standing up a server
```

---

## 5. Judgment meets an unattended trigger

> "Post a summary of yesterday's commits to Slack every morning at 9am."

The conflict from `signals.md`: a clock trigger wants determinism, but
summarizing commits into prose is irreducibly judgment.

```
Build:        A scheduled task
Plus:         A skill supplying the summarization judgment, and a script or
              MCP call for the Slack write
Don't build:  A pure cron script — it would post a git log, which is what you
              already have and not what you want
Because:      For — turning a diff into an audience-appropriate narrative
              can't be expressed as code
Confidence:   Medium
Flips if:     A templated digest turns out to be good enough. Then it's a
              plain script and no model is needed
```

Medium, not High: this is a case where judgment sits *on* the unattended path,
which is normally a smell. It's acceptable here only because a bad summary is
low blast radius — nobody gets paged over a mediocre standup post.

---

## 6. A genuine close call

> "Make a chart from a CSV."

```
Build:        Undetermined — one question settles it
Plus:         —
Don't build:  Anything yet
Because:      No decisive signal fired in either direction
Confidence:   Close call
Flips if:     Answered either way by: "Do you always want the same chart type,
              or should the encoding be chosen from the data's shape?"
              Always the same  → script, matplotlib, done
              Chosen from data → skill, because picking an encoding is judgment
```

Guessing here would be wrong half the time. Ask.

---

## 7. Audit of an existing skill

> `~/.claude/skills/image-collage`

Measured first, via `scripts/audit_skills.py`:

```
body_lines: 48
undocumented_flags: {"scripts/collage.py": ["--align", "--scale"]}
git_dirty: true
```

```
Grade:        Thin wrapper — correct shape, drifting execution
Because:      The shape is right: a 48-line body over a 200-line deterministic
              script is the composition from example 1. But two flags exist in
              code and in no markdown, and the working copy is uncommitted, so
              the published repo documents a version that no longer exists
Remediation:  1. Delete the flags section from SKILL.md and README; point at
                 --help instead. One source of truth
              2. Keep only what --help can't say: the ordering convention, and
                 the "when NOT to use this" list — the most valuable content
                 there
              3. Commit the outstanding work so the public copy matches
Confidence:   High
Flips if:     The script grows genuine judgment — auto-detecting subject
              placement, say. Then the skill body earns more space
```

Note what the audit did **not** do: grade it as justified merely because it works.
The question is whether the shape is right, not whether it runs.
