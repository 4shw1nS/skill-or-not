# Evals

29 labeled cases in `cases.jsonl`, 22 of them blind-runnable, plus three
[audit-mode fixtures](fixtures/README.md). They exist to make changes to the
rubric measurable — if you edit `reference/signals.md`, run these before and
after and see what moved.

## Case format

| Field | Meaning |
|---|---|
| `id` | Short handle |
| `input` | What a user would actually say |
| `expected_primary` | The shape that should lead the verdict |
| `expected_composition` | Shapes that should also appear |
| `expected_not` | Shapes the verdict must **not** recommend — the tempting wrong answer |
| `decisive_signal` | Which signal should fire, and in which direction |
| `blind_runnable` | False when the case is settled by something already installed |
| `notes` | Why this case is in the set |

### `blind_runnable`

Seven cases describe capabilities the author already has installed. On that
machine Step 0 finds the existing artifact and terminates before the gates run,
so the case measures prior-art detection rather than the shape decision it was
written for. They stay in the set because they remain valid **design checks** —
walk them through the gates on paper — but a blind run of one on a machine that
has the capability proves nothing.

This was found the hard way: a blind run of `img-merge` returned "you already
built this", which is correct behavior and a non-result. Check the flag before
choosing a batch. A case is blind-runnable on *your* machine only if nothing
installed already solves it — the flag records the author's environment, not
a universal property.

## Running them

Run a case by opening a fresh session and giving it the `input` verbatim, then
compare the verdict against the labels. `run_evals.py` automates the fresh
sessions and the mechanical half of the grading; the judgment half stays with
you (or, with `--judge`, gets a second model's opinion recorded beside it).

```bash
python3 run_evals.py --dry-run           # list what would run
python3 run_evals.py                     # all blind-runnable cases
python3 run_evals.py --cases resize-800,uuid-gen
python3 run_evals.py --judge             # also grade the Because: line
```

Each case gets a fresh `claude -p` session in an empty temp directory, so no
project context leaks in and no two cases share a session. Per case the runner
auto-checks three things: the skill **fired**, the `Build:` line matches
`expected_primary`, and nothing in `expected_not` appears in `Build:`/`Plus:`
(`Don't build:` may name them — that's its job). Whether the `Because:` line
matches `decisive_signal` is judgment; the runner prints both side by side,
or grades it with a second model under `--judge` (`--judge-model`, default
opus — the judge's false-YES rate is what hides regressions, so don't
economize here). Transcripts and `results.json` land in `results/<timestamp>`
(`--outdir` overrides). `--model` picks the model under test,
`--include-non-blind` adds the cases Step 0 would pre-empt on the author's
machine, `--claude-bin`, `--claude-arg`, and `--timeout` control the CLI
invocation itself.

Treat auto-grades as a screen, not a court. `MANUAL` rows and any `FAIL` that
surprises you deserve a human read of the saved transcript — pattern-matching
a verdict line is cheaper than judgment, not a replacement for it. The two
ask-cases (`support-triage`, `csv-chart`) are always `MANUAL`: a single `-p`
turn can't answer the clarifying question they exist to provoke.

After editing the grader or a case's *labels*, re-grade the saved transcripts
instead of paying for new sessions: `--regrade results/<timestamp>` (writes
`results-regraded.json` alongside). A transcript is only reusable while the
case's `input` is unchanged — a reworded input needs a fresh run.

The first full run of this harness (2026-08-13) is a cautionary tale worth
keeping: 11 of 23 cases auto-failed, and on inspection *zero* of the eleven
were rubric defects — four were grader bugs, two were judge false-NOs, one was
a stale `blind_runnable` flag, three were label defects the rubric outsmarted
(`pr-triage`'s "each morning" really is a clock; `license-sweep`'s scanner
work really is a script), and one was the ask-case limitation above. The
harness's first real product was better labels, not a rubric grade.

### Why every input is phrased as a design question

Each `input` asks *how something should be built*, never *do this thing*. That
distinction is load-bearing, and it was learned the hard way: an earlier version
phrased them as tasks — "Stop Claude from ever running rm -rf on my machine" —
and in a blind run the skill correctly did not fire. Another skill took it and
set a deny rule, which was the right outcome.

An imperative is a request to act. Firing a six-axis classifier at one would
wedge a framework between the user and a one-line change. **A case phrased as a
task tests Claude's default behavior, not this skill** — and if you add one, it
will look like a trigger failure when it is really a miscategorized case.

Test the trigger surface separately from the verdict: check whether the skill
engages at all before grading what it said. Real requests rarely arrive
pre-labeled as design questions, so silent non-firing is the failure mode most
worth watching.

### Why the actor is pinned in most inputs

The skill asks up to three clarifying questions, which means an input leaving an
axis unstated is **not a reproducible trial** — different answers produce
different correct verdicts, and the label only describes one branch. Four cases
in one batch drifted off their labels this way, all of them on the actor axis.

So inputs state who performs the work unless the ambiguity *is* the test.
`support-triage` and `csv-chart` stay deliberately underspecified, because
asking rather than guessing is what they measure.

Pinning also changes what a case tests. `bigquery-conventions` pinned to one
person exercises G5 (reach); the same case with analysts querying the tables
makes G0 fire first and lands on database views instead. Both verdicts are
right — they answer different questions. If you loosen a pin, expect the gate
under test to change with it.

A case **passes** when the primary shape matches, nothing from `expected_not`
appears, and the stated reason matches `decisive_signal`. Getting the right
answer for the wrong reason is a fail — it means the rubric didn't do the work
and won't generalize.

Grade on a fresh session each time. Once a skill's body is in context it stays
there, so a second case in the same session isn't an independent trial.

## What the set covers

- **Ground truth** (5): drawn from skills already built, where the correct
  shape is known from experience rather than argued from the rubric
- **Adversarial** (9): cases that look like one shape and are another —
  `prettier-on-save` looks like a skill and is a hook; `internal-wiki-search`
  looks like knowledge and is a reach problem; `untested-endpoints` looks like
  a Claude problem and is a human one
- **Null verdicts** (3): cases where the answer is build nothing
- **Composition** (7): cases where a single-shape verdict is wrong
- **Close call** (2): `support-triage` and `csv-chart`, where the correct
  behavior is to ask rather than commit
- **Gate coverage** (3): `license-sweep` (G6, the only subagent verdict),
  `pnpm-not-npm` (G3's always-true branch, the only CLAUDE.md-primary verdict),
  and `legacy-billing-quirks` (G8's model-only branch, where the invocation
  setting is part of the pass criteria)

Modes B and C are covered separately: three deliberately flawed fixture skills
with labeled grades live in [`fixtures/`](fixtures/README.md). Sweeps skip
them by design; audit one by passing its path directly.

## The self-reference case

`self-reference` is this skill judging itself. It must come out as *skill +
script*: the audit measurement is deterministic and belongs in code, the
adjudication is not. If that case ever fails, the rubric is wrong — fix the
rubric, not the case.

## Adding cases

Add one whenever a real verdict turns out wrong. Record what was actually said,
what the right answer was, and which signal should have fired. Cases earned from
real misses are worth more than invented ones.
