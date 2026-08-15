# Audit-mode fixtures

Five deliberately flawed skills with known correct grades. The greenfield
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
and graded to label for the labeled reason. A Mode C sweep the same day —
these three fixtures plus a genuinely justified skill as a control — fired
unprompted and graded 4/4 to label with the correct ranking, covering
`should-be-script` and confirming the sweep discriminates rather than
condemning everything. A good sweep control is a real skill you believe in;
if the sweep can't tell it from the fixtures, the sweep is worthless.

## External blind trial (2026-08-15)

The first trial against skills nobody here wrote or labeled: six third-party
skills — two from `anthropics/skills` (docx, slack-gif-creator) and four from
`ComposioHQ/awesome-claude-skills` (video-downloader, raffle-winner-picker,
changelog-generator, domain-name-brainstormer) — copied under neutral names
with authorship stripped, expected grades pre-registered before any session
ran. Six fresh Mode B sessions plus one Mode C sweep, all fired unprompted.

Results: **5/6 grades matched the pre-registered labels for the labeled
reason**, and the sweep ranked all six correctly (both Anthropic skills
survived as Justified — the controls held). The audits also surfaced
verified-real defects: a validator in slack-gif-creator that computes file
size and then ignores it in its pass/fail, a hardcoded claude.ai container
path as video-downloader's default output directory, and
raffle-winner-picker shipping no code while promising "cryptographically
random" selection.

The one miss was the pre-registered label, not the verdict:
changelog-generator was labeled Justified because the *task* is judgment,
but the audit graded the *artifact* — a body with no procedure, no
conventions, no delta over the base model — as Delete-or-rewrite, which is
what Mode B's "run the gates against what the skill actually does" actually
instructs. The two fixtures below (`prompt-brochure`, `unbacked-reach`)
encode the two antipatterns this trial found that the original fixture set
did not cover. One internal inconsistency to watch: Mode B graded the
brochure pattern Delete-or-rewrite while the same day's sweep said Thin
wrapper — adjacent grades, identical remediation, but the wobble is real.

Caveats: one finding (a name/content mismatch in the de-identified
slack-gif-creator copy) was an artifact of the rename and excluded from
scoring; and expected grades were pre-registered by the same model family as
the system under test, so the 5/6 is a consistency measure, not independent
ground truth.

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

## `prompt-brochure/`

**Expected grade: Delete** (as written) — with rewrite-if-conventions-exist
as acceptable nuance. From the 2026-08-15 external trial (the
changelog-generator pattern).

The shape passes the gates: writing PR descriptions is real judgment,
invoked sometimes, person-triggered. What fails is the body — it is a
brochure *about* the skill, not instructions *for* it. "What This Skill
Does" states outcomes with no procedure, "How to Use" is example prompts for
the user to type (the wrong audience — Claude reads SKILL.md, the user
never does), and nothing in the file changes what the model would produce
unprompted. A zero-delta body is an empty carrier: it pays trigger-surface
rent and returns base-model behavior.

**Expected reason:** the body adds no delta over default model behavior —
not prior art, not missing judgment. The right grade for the wrong reason
is a fail: this is *not* a thin wrapper (there is no script to wrap) and
*not* should-be-deterministic (the task genuinely needs a model).

**Expected remediation:** delete, or rewrite to ~20 lines that are all
delta: exact git commands, the team's section template, explicit noise
filters. Also flag the marketing description ("Saves you from writing PR
descriptions ever again") occupying every session's system prompt.

**Adjacent-grade wobble is known:** the live trial graded this pattern
Delete-or-rewrite in Mode B and Thin wrapper in Mode C. Either passes if
the reason is zero-delta; grading it Justified fails.

## `unbacked-reach/`

**Expected grade: Delete** (or rebuild as script + thin skill). From the
2026-08-15 external trial (the domain-name-brainstormer pattern).

The skill's one differentiating promise — look up each dependency in the
CVE database — requires external reach, and the skill ships no mechanism:
no script, no API call, nothing. Prose cannot query a database, so the
worked example's ✓/✗ table with CVE ids and severities is a template for
*fabricating* security findings. That makes it worse than useless: a
security answer that looks verified and isn't. G5 is the decisive gate —
reach is the whole problem, and a skill cannot grant it.

**Expected reason:** promised capability requires reach with no mechanism
shipped; the example output coaches hallucination. Missing the
fabrication-coaching point but landing Delete on reach alone is
partial credit; grading it Justified or Thin wrapper is a fail — there is
nothing underneath to wrap.

**Expected remediation:** a script querying a real vulnerability API or
running an existing scanner (`npm audit`, `osv-scanner` — prior art may
delete even the script), plus at most a thin skill that maps intent onto
it and never asserts findings it didn't fetch.
