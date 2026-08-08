# skill-or-not

Decide whether a problem, workflow, or intent should become **a skill, a script,
a CLI, a hook, a subagent, an MCP server, a scheduled job, a plugin — or nothing
at all.** Then audit the skills you already have to see whether their shape is
still right.

```
"should this be a skill?"  →  five axes  →  eight gates  →  a verdict with a falsifier
```

The default answer is **no**. The gate order puts the burden of proof on building
a skill, because the usual failure isn't picking the wrong mechanism — it's
building something where nothing was needed.

> **Status: v0.1, unverified.** The rubric has been checked against all 22 eval
> cases with the answer key visible, which validates that the gates yield the
> labeled shape. It has **not** been measured on blind runs in fresh sessions,
> so there is no evidence yet about how it behaves on a case it wasn't tuned
> against. Treat the verdicts as arguments, not measurements.

---

## Try it in 30 seconds

```bash
git clone https://github.com/<you>/skill-or-not.git
cp -R skill-or-not ~/.claude/skills/
```

In Claude Code, describe a workflow and ask whether it should be a skill, or:

```
/skill-or-not audit ~/.claude/skills/some-skill
/skill-or-not sweep ~/.claude/skills
```

The audit script is standalone and needs only Python 3 — no dependencies:

```bash
python3 ~/.claude/skills/skill-or-not/scripts/audit_skills.py ~/.claude/skills
```

---

## Why five axes instead of a list

"Skill or plugin?" and "skill or MCP?" are category errors — those live on
different axes and **compose**. A classifier built on a flat menu of options is
confidently wrong on exactly the cases that matter.

| Axis | Question |
|---|---|
| ⚖️ **Judgment** | Is there a decision between the request and the command? |
| ⏱ **Trigger** | A person, Claude, a file event, a clock, or a push? |
| 🧠 **Context** | Main thread, isolated subagent, or outside Claude entirely? |
| 🔌 **Reach** | Local files, or an authenticated external system? |
| 📦 **Distribution** | One person, a team, or the public? |

Shapes on the same axis compete. Shapes on different axes compose. Most correct
verdicts name two or three.

---

## What comes out

```
Build:        <primary shape>
Plus:         <composition, or "nothing else">
Don't build:  <the tempting wrong answer, and why>
Because:      <one named decisive signal>
Confidence:   High | Medium | Close call
Flips if:     <the falsifier>
```

Every verdict names **one** decisive signal, not a pile of weak ones, and states
what would change it. "Close call" is a permitted answer — where no signal fires,
the useful response is the question that would settle it.

---

## Three modes

| Mode | Input | Output |
|---|---|---|
| **Greenfield** | A problem, workflow, or intent | A verdict, and an offer to scaffold |
| **Audit** | One existing skill | A grade, with line-level remediation |
| **Sweep** | A skills directory | Every skill ranked by how well it justifies its context cost |

---

## The audit script

Audit and sweep have a mechanical half — counting, parsing, drift detection —
and a judgment half. `scripts/audit_skills.py` does only the first, and the model
judges its JSON. That split is the same one this skill recommends to everyone
else, applied to itself.

It measures frontmatter validity against the published limits, body length,
third-person descriptions, missing trigger phrases, uncommitted changes, and
**documentation drift**: flags a script accepts that no markdown file mentions.

---

## File map

```
skill-or-not/
├── SKILL.md                  ← Claude reads this (~130 lines, deliberately)
├── README.md                 ← this file
├── reference/
│   ├── shapes.md             ← every shape, its real cost, its decisive signal
│   ├── signals.md            ← the rubric, and how to resolve conflicts
│   └── antipatterns.md       ← failure modes, in artifacts and in judging
├── examples/
│   └── worked-examples.md    ← seven worked verdicts
├── scripts/
│   └── audit_skills.py       ← measurement only; stdlib, no dependencies
└── evals/
    ├── cases.jsonl           ← 22 labeled cases
    └── README.md             ← how to grade them
```

SKILL.md stays near 130 lines on purpose. A skill body enters the conversation on
invocation and **stays there for the rest of the session** — so length is a
recurring cost paid on every later turn, including all the turns that have
nothing to do with it. Everything conditional lives in `reference/`, read only
when needed. A skill that bloated its own context while preaching restraint would
fail its own audit.

---

## When NOT to use this

- **You already know the answer.** The gates are for genuine uncertainty.
- **The thing is trivial and one-off.** Below roughly three repetitions,
  formalizing anything costs more than it saves — and this skill will tell you
  that, which you could have skipped asking.
- **It's a safety requirement.** Those go to hooks and permission rules. You
  don't need a classifier to tell you a wall beats a suggestion.

---

## License

[MIT](LICENSE) © Ashwin Sinha
