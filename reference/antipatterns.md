# Antipatterns

Failure modes in the artifacts people build, and failure modes in the judging
itself. Both are worth checking.

## Contents

- [Build antipatterns](#build-antipatterns)
- [Judging antipatterns](#judging-antipatterns)
- [Audit checklist](#audit-checklist)

---

## Build antipatterns

### The `--help` mirror
A skill body that restates the flags its own script already documents. Two
sources of truth, and the prose one always loses. Seen in the wild: a script
gained two new flags; its SKILL.md and README documented neither for six weeks,
and the published repo kept serving the stale copy to everyone who cloned it.

**Spot it:** `audit_skills.py` reports undocumented flags.
**Fix:** point at `--help`. Document only what `--help` can't say — when to use
which flag, and why.

### The pinned encyclopedia
A skill body that keeps growing because reference material got appended to it.
The body stays in context for the whole session once loaded, so every unrelated
turn afterward pays for it.

**Spot it:** body over ~200 lines, most of it reference rather than procedure.
**Fix:** move reference into `reference/*.md`, linked one level deep from
SKILL.md. Files cost nothing until read.

### The suggestion posing as a guardrail
A skill that says "never commit to main" or "always validate before writing."
Instructions are advisory; the model may not comply.

**Fix:** hooks and permission rules for anything load-bearing. Keep the skill for
guidance that's genuinely advisory.

### The model in the cron job
Scheduling something whose critical path needs judgment. It works until the day
it silently doesn't, and nobody's watching.

**Fix:** schedule the deterministic part; keep judgment interactive.

### The wrapper around a solved problem
A skill for something `sips`, `jq`, `gh`, or a built-in already does. Costs
permanent description context and adds a layer that can drift.

**Fix:** Step 0. Always.

### The always-loaded procedure
A multi-step procedure living in CLAUDE.md, loaded on every turn of every session
even when irrelevant.

**Fix:** move it to a skill. CLAUDE.md is for facts that are always true.

### The premature plugin
Manifest, version, namespace, and marketplace listing for something one person
uses on one machine.

**Fix:** standalone `.claude/` until a second person actually needs it.

### The subagent used for brainpower
Delegating to a subagent expecting better thinking. Subagents start cold and must
re-derive context you already have — often worse, always slower.

**Fix:** subagents for parallelism and context hygiene only.

### The description that doesn't say when
`description: Processes data.` Claude selects skills from descriptions alone. One
that omits triggers will not fire when it should.

**Fix:** state what it does **and** when to use it, in third person, with the
phrases a user would actually type.

---

## Judging antipatterns

Failure modes in applying this rubric.

### Verdict-first reasoning
Forming an opinion, then finding signals to support it. The axis table exists to
prevent this and only works if filled in before the verdict.

### Signal stacking
Piling up four weak arguments in place of one decisive signal. If no decisive
signal fired, the honest verdict is *close call* — not a confident answer
assembled from weight signals.

### The forced binary
Answering "skill or script?" as posed when the real answer is both. Composition
is the most common correct verdict.

### Category confusion
Comparing shapes on different axes — "skill or plugin?", "skill or MCP?". These
compose. Only same-axis shapes compete.

### Deference to the framing
Someone asking "should this be a skill?" has usually already decided. Agreeing is
the path of least resistance and often wrong.

### Ignoring the null option
Forgetting that "build nothing" is available, and that it wins more often than
anyone expects.

### Sunk-cost auditing
In audit mode, grading something as justified because it already exists and works.
The question is whether the shape is right, not whether it runs.

---

## Audit checklist

Run `scripts/audit_skills.py` for the measurable half, then judge the rest.

**Measured by the script:** frontmatter validity · name/description limits ·
third-person description · trigger phrases present · body line count ·
undocumented script flags · uncommitted changes.

**Requires judgment:**
- Does the body earn its permanent context cost, or is it a `--help` mirror?
- Would a decisive-against signal fire if this were proposed fresh today?
- Is the invocation setting right — should a side-effecting skill really be
  model-invocable?
- Do the reference files get read, or are they decoration?
- Is anything here a suggestion that should be enforcement?
