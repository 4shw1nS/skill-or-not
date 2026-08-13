# Audit-mode fixtures

Three deliberately flawed skills with known correct grades. The greenfield
cases in `cases.jsonl` test Mode A; these test Modes B and C. Each is small,
broken in exactly one interesting way, and labeled below.

Sweeps never discover them: `audit_skills.py` excludes directories named
`fixtures`, precisely so these don't pollute a real sweep. Audit one by
passing its path directly:

```bash
python3 ../../scripts/audit_skills.py help-mirror --format json
```

To run a Mode B trial, open a fresh session and ask:
`audit <absolute path to the fixture>` — then compare the verdict to the
labels here. As with the greenfield cases, the right grade for the wrong
reason is a fail.

For a **blind** trial, copy the fixture somewhere neutral first and rename
both the directory and the frontmatter `name` — the names here (`help-mirror`,
`prior-art-wrapper`) leak their own grades, and a live trial called that out
unprompted. Run from inside the copy's parent directory so a headless
session's file sandbox can reach it. Headless sessions also can't approve the
audit script's Bash prompt; at fixture size a hand count is equivalent, but
interactive trials exercise the script path too.

First blind trials (2026-08-13, fresh headless sessions, de-identified
copies): `help-mirror` and `prior-art-wrapper` both fired Mode B unprompted
and graded to label for the labeled reason. `should-be-script` has not had a
blind trial yet.

## `help-mirror/`

**Expected grade: Thin wrapper** — right shape, drifting execution.

The shape is correct: a script owns the work, a small skill maps intent onto
it. But the body restates `--width`, `--height`, and `--color`, which
`--help` already documents — and the script's `--gap` flag appears in no
markdown at all. That undocumented flag is the measurable symptom the audit
script must report; the `--help` mirror is the judgment half.

**Expected remediation:** point at `--help`; keep only what it can't say
(the busy-image vs portrait guidance is the one line worth keeping).

**Secondary defect** (unlabeled originally; a blind trial caught it): the
example commands use paths relative to the skill directory, which break when
the skill fires from the user's working directory. A full-credit audit
mentions it; missing it is not a fail.

The `name does not match directory` complaint the script may emit when the
fixture is copied elsewhere is incidental, not the point of the fixture.

## `should-be-script/`

**Expected grade: Should be deterministic.**

Four fixed commands, zero decisions, and the body even says "do not vary the
sequence." An identical invocation every time is the decisive-against signal;
a fragile fixed sequence wants an exact script, not model discretion —
especially with an `rm -rf` as step four.

**Expected remediation:** move the sequence into a shell script. A near-empty
user-invocable skill in front of it is optional, only if archiving is
invoked through Claude at all.

## `prior-art-wrapper/`

**Expected grade: Delete.**

`sips` ships with macOS and ImageMagick does it everywhere else — the skill
body admits as much by quoting both. Prior art settles it at Step 0: the
description pays permanent system-prompt rent to wrap a one-liner.

**Expected remediation:** delete; a shell function if the conversion is
frequent.
