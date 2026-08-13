---
name: skill-or-not
description: >
  Decides whether a problem, workflow, or user intent should become a skill, a
  script, a CLI, a hook, a subagent, an MCP server, a scheduled job, a plugin,
  or nothing at all — and audits existing skills for whether their shape is
  still right. Use when the user asks "should this be a skill?", "how should I
  build this?", "skill or script?", "what's the right mechanism for this?",
  "what shape should this take?", "is this worth automating?", "am I
  over-engineering this?", "audit my skills", "which of my skills shouldn't be
  skills?", or invokes /skill-or-not.
---

# Skill or Not

Place the candidate on six axes, run the gates in order, name the composition.
Most correct answers are a combination of mechanisms, not a single one.

## Modes

| Input | Mode |
|---|---|
| A problem, workflow, or intent | **A — Greenfield** |
| A path to one existing skill | **B — Audit** |
| A skills directory or repo | **C — Sweep** |

If the input could be A or B, ask. Do not guess.

## Mode A — Greenfield

### Step 0: Prior art

Before any recommendation, establish that this doesn't already exist. Check for
a standard CLI, a built-in command, an existing skill in the user's setup, or a
library. **"Build nothing, use X" is a valid and frequently correct verdict.**
If prior art covers the whole request, emit that verdict and stop — the gates
below are only for what it leaves unsolved. Skipping this step is the single
most expensive error available here.

### Step 1: The six axes

Fill this table explicitly before forming any opinion. Reasoning that starts
with a verdict and backfills justification is the main failure mode.

| Axis | Question | Answer |
|---|---|---|
| **Actor** | Whose behavior must change — Claude's, a human's, or both? | |
| **Judgment** | Is there a decision between the request and the command? | |
| **Trigger** | What starts it — a person, Claude, an event, a clock, a push? | |
| **Context** | Main thread, isolated subagent, or outside Claude entirely? | |
| **Reach** | Local files only, or an authenticated external system? | |
| **Distribution** | Just this user, a team, or public? | |

If an axis can't be answered from the request, ask — up to three questions,
then proceed on stated assumptions.

### Step 2: The gates

Run **all** of them, in order. A gate answering "no" never ends the run — later
gates catch cases earlier ones route past.

**G0 — Actor.** Whose behavior must change? Every Claude-side mechanism — skill,
hook, CLAUDE.md, permission rule — governs **Claude and nobody else**. If the
behavior belongs to humans (or to other tools they use), none of them reach it:
route to **CI, a linter, a process change, or documentation**. If it belongs to
both, pick the mechanism that catches both, which is almost always CI.

> Ask this literally: who performs the action you want changed? "Engineers keep
> committing X" is not a Claude problem, however much it feels like one.

**G1 — Enforcement.** Must this be impossible to bypass — safety, secrets,
destructive commands? → **hook + permission rules**, and stop. Instructions are
advisory and a model can be argued out of them, so this overrides G2 even when
judgment is genuinely involved. A skill may add guidance on top, never instead.

**G2 — Judgment.** Is there a decision a model must make between the request and
the command?
- **No** → deterministic code owns the work. Keep going; the remaining gates
  still apply, and one of them may still put a model beside it.
- **Yes** → a model belongs somewhere in the loop.

**G3 — Fact or procedure.** Only if G2 was yes. True on every turn, with no
steps → **CLAUDE.md**, and it costs context on every turn, so be sure. Invoked
sometimes, and has steps → **skill**. A CLAUDE.md section that has grown steps
has become a skill; move it.

**G4 — Trigger.** A tool or file event → **hook**. A clock → **scheduled task**.
A push or PR → **CI**. A person, in conversation → **user-invocable skill** or
**CLI**. Claude noticing relevance → **model-invocable skill**.

> If G2 said "judgment required" and G4 says "unattended", that is a conflict.
> Resolve it by blast radius, not by reflex. Where a silent failure does real
> damage — deploys, money, data loss — split it: the deterministic core runs
> unattended and the judgment stays interactive. Where a degraded result is
> merely unhelpful, a scheduled model run is legitimate; say so, and mark the
> verdict Medium rather than High.

**G5 — Reach.** Authenticated external system, reusable across tasks → **MCP
server**. Single-purpose external call → **script holding the credential**.
Reach is not knowledge: MCP grants access but teaches nothing, so anything
needing both takes MCP **plus a knowledge carrier** — and G3 decides whether
that carrier is CLAUDE.md or a skill. Do not assume a skill; two standing facts
belong in CLAUDE.md.

**G6 — Context.** Needs isolation, parallel fan-out, or produces output that
would flood the main thread → **subagent**, or a skill with `context: fork`.

**G7 — Distribution.** One user → `~/.claude/`. A team or several repos →
**plugin**. Public → plugin plus a marketplace. Packaging is an independent
axis; it never replaces the mechanism chosen above.

**G8 — Invocation.** Only if a skill survived. Side effects or timing the user
must control → `disable-model-invocation: true`. Background knowledge that isn't
an action → `user-invocable: false`. Otherwise leave both default.

### Step 3: Verdict

```
Build:        <primary shape>
Plus:         <composition, or "nothing else">
Don't build:  <the tempting wrong answer, and why it's wrong>
Because:      <the signal that actually ended the run>
Confidence:   High | Medium | Close call — split it per part when they differ
Flips if:     <the falsifier>
```

**`Because:` must name the gate or step that actually terminated the run**, not
the most familiar one. If Step 0 ended it, the reason is prior art. If G0 ended
it, the reason is that the actor is not Claude. If G4 ended it, the reason is
the trigger. Defaulting to "no judgment" whenever G2 happened to be *involved*
is the common error — G2 is the reason only when G2 is what settled it.

Split `Confidence:` when the parts differ: a composition can be High on the
script and Medium on whether the skill half is worth writing at all.

Then offer to scaffold. Do not scaffold unasked.

## Mode B — Audit

1. Run `python3 scripts/audit_skills.py <path> --format json` for measured
   facts. The script lives in this skill's own directory — resolve it from
   where this SKILL.md was loaded, not the working directory. Do not eyeball
   what the script can count.
2. Run the same six axes and gates against what the skill actually does.
3. Grade: **Justified** · **Thin wrapper** (skill layer earns less than it
   costs) · **Should be deterministic** · **Should be packaged** · **Delete**.
4. Give specific remediation, with line references.

A thin wrapper is not automatically wrong. A skill whose only job is mapping
fuzzy intent onto a script's flags is legitimate — provided its body stays
near-empty and doesn't duplicate `--help`.

## Mode C — Sweep

Run the audit script across the directory, then rank by how well each skill
justifies its permanent context cost. Report as a table: skill, body lines,
grade, one-line reason. Call out sprawl explicitly — every model-invocable
skill's description occupies the system prompt in every session, used or not.

## Rules that keep this accurate

- Fill the axis table **before** forming a verdict.
- The default is *don't build a skill*. It must earn it with a decisive signal.
- Name **one** decisive signal, not a pile of weak ones.
- Every verdict states a falsifier.
- "Close call" is a permitted confidence. Do not manufacture certainty.
- Composition is normal, not a hedge. "Script plus thin skill" is a real answer.
- Recommend against the user's framing when warranted. Someone asking "should
  this be a skill?" has usually already decided; the useful answer is often no.

## References

- **[reference/shapes.md](reference/shapes.md)** — every shape, its real cost, its decisive signals
- **[reference/signals.md](reference/signals.md)** — the full rubric and how to resolve conflicts
- **[reference/antipatterns.md](reference/antipatterns.md)** — known failure modes
- **[examples/worked-examples.md](examples/worked-examples.md)** — worked verdicts in the output format
- **[evals/cases.jsonl](evals/cases.jsonl)** — labeled cases for measuring changes to this rubric
