# Evals

22 labeled cases in `cases.jsonl`. They exist to make changes to the rubric
measurable — if you edit `reference/signals.md`, run these before and after and
see what moved.

## Case format

| Field | Meaning |
|---|---|
| `id` | Short handle |
| `input` | What a user would actually say |
| `expected_primary` | The shape that should lead the verdict |
| `expected_composition` | Shapes that should also appear |
| `expected_not` | Shapes the verdict must **not** recommend — the tempting wrong answer |
| `decisive_signal` | Which signal should fire, and in which direction |
| `notes` | Why this case is in the set |

## Running them

There is no automated runner; grading requires judgment, which is the point.
Run a case by opening a fresh session and giving it the `input` verbatim, then
compare the verdict against the labels.

### Why every input is phrased as a design question

Each `input` asks *how something should be built*, never *do this thing*. That
distinction is load-bearing, and it was learned the hard way: an earlier version
phrased them as tasks — "Stop Claude from ever running rm -rf on my machine" —
and in a blind run the skill correctly did not fire. Another skill took it and
set a deny rule, which was the right outcome.

An imperative is a request to act. Firing a five-axis classifier at one would
wedge a framework between the user and a one-line change. **A case phrased as a
task tests Claude's default behavior, not this skill** — and if you add one, it
will look like a trigger failure when it is really a miscategorized case.

Test the trigger surface separately from the verdict: check whether the skill
engages at all before grading what it said. Real requests rarely arrive
pre-labeled as design questions, so silent non-firing is the failure mode most
worth watching.

A case **passes** when the primary shape matches, nothing from `expected_not`
appears, and the stated reason matches `decisive_signal`. Getting the right
answer for the wrong reason is a fail — it means the rubric didn't do the work
and won't generalize.

Grade on a fresh session each time. Once a skill's body is in context it stays
there, so a second case in the same session isn't an independent trial.

## What the set covers

- **Ground truth** (5): drawn from skills already built, where the correct
  shape is known from experience rather than argued from the rubric
- **Adversarial** (7): cases that look like one shape and are another —
  `prettier-on-save` looks like a skill and is a hook; `internal-wiki-search`
  looks like knowledge and is a reach problem
- **Null verdicts** (3): cases where the answer is build nothing
- **Composition** (6): cases where a single-shape verdict is wrong
- **Close call** (1): `csv-chart`, where the correct behavior is to ask

## The self-reference case

`self-reference` is this skill judging itself. It must come out as *skill +
script*: the audit measurement is deterministic and belongs in code, the
adjudication is not. If that case ever fails, the rubric is wrong — fix the
rubric, not the case.

## Adding cases

Add one whenever a real verdict turns out wrong. Record what was actually said,
what the right answer was, and which signal should have fired. Cases earned from
real misses are worth more than invented ones.
