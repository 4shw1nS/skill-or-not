# Signals

The rubric. Decisive signals settle a case on their own; weight signals only
break ties. There is no numeric score — inventing one would manufacture
precision this judgment doesn't have.

## Contents

- [Diagnostic questions](#diagnostic-questions)
- [Decisive against a skill](#decisive-against-a-skill)
- [Decisive for a skill](#decisive-for-a-skill)
- [Weight signals](#weight-signals)
- [Resolving conflicts](#resolving-conflicts)
- [Calibrating confidence](#calibrating-confidence)

---

## Diagnostic questions

Ask these of the candidate. Each answer maps to a signal below.

1. **Between the user's request and the command that runs, what decision gets made?**
   If the honest answer is "none", the case is over — it's deterministic code.
2. **Could a shell script with the right flags do this, if someone told it the flags?**
   If yes, the only question left is whether choosing the flags needs a model.
3. **What starts it?** A person, Claude noticing, a file event, a clock, a push.
4. **Does it need to see anything before deciding?** Repo state, prior output,
   the user's history, external data.
5. **What happens if it's wrong?** A bad suggestion, or a bad deploy.
6. **How often, and by whom?**
7. **Does it already exist?**

## Decisive against a skill

Any one of these settles it. Do not accumulate counter-arguments.

| Signal | Verdict |
|---|---|
| **The actor is human, not Claude** | CI, linter, process, docs |
| **An installed skill already claims these triggers** † | extend it, don't add a second |
| **Runs unattended** — no human or model present at runtime | script + hook/cron/CI |
| **Identical invocation every time** | alias |
| **Needs reproducibility, speed, or bulk** | script |
| **Arguments fully determined by the request** | CLI |
| **Enforcement must be unbypassable** | hook + permissions |
| **Prior art exists** | build nothing |
| **The rules are already encoded in a linter/formatter/validator** | run that tool |

† A special case of prior art, not independent of it — see below.

**On the actor signal.** Skills, hooks, CLAUDE.md, and permission rules all
constrain Claude alone. A teammate who hand-writes the violation, uses a
different editor, or pastes from the web never encounters them. When the
behavior you want to change belongs to people, the only mechanism that reaches
both them and the model is one that sits in shared infrastructure — CI, a
pre-commit hook in the repo, a linter everyone runs. Wanting a Claude-side fix
for a human problem is one of the easiest mistakes to make here, because the
request arrives while you are already talking to Claude.

**On the duplicate-trigger signal.** This is a *refinement of prior art*, not an
independent signal, and it will almost never be the reason a verdict lands. If
another skill claims your trigger phrases, that skill **is** prior art, so Step 0
fires first and settles the case. What duplicate-trigger adds is the specific
consequence: two model-invocable skills matching the same phrases both pay
permanent system-prompt rent, and which one fires is not something you control.
Name it as a supporting reason; expect prior art to be the primary one.

**Testing whether two candidates are really one.** Fill the axis table for the
proposed sibling and compare it against the incumbent's. If every row matches,
the difference between them is *what to look for*, not *how the work is shaped*
— and that is an argument to the existing thing, not a new one.

> Content differences are arguments; mechanism differences are new skills.

A performance reviewer and a security reviewer have identical actors, triggers,
reach, and distribution. They differ only in which patterns they hunt. That is
one skill with a focus argument, or a reference file — never two skills fighting
over "review my PR".

## Decisive for a skill

Any one of these justifies the context cost.

| Signal | Why code can't do it |
|---|---|
| **Must read ambient context before deciding** | a script can't look around first |
| **Encodes taste or convention that can't be flags** | there's no `--house-style` |
| **Branches on the meaning of prose** | classification requires a model |
| **Composes mid-conversation with other work** | a CLI ends; a conversation continues |
| **Input format is unknown until seen** | normalizing is the hard part |
| **Output needs interpretation, not just delivery** | "here's what this means" |

## Weight signals

These never decide alone. Use them to break a genuine tie.

- **Frequency.** Under three repetitions, formalizing costs more than it saves.
- **Users.** One person tips toward personal and lightweight; a team tips toward
  packaged and documented.
- **Blast radius.** Irreversible effects tip toward user-invocable and a fixed
  script, away from model discretion.
- **Drift risk.** The more flags a script has, the more a prose wrapper will rot.
  Prefer pointing at `--help` over restating it.
- **Context cost.** A long body is a recurring tax on every later turn in the
  session. A skill that would need 400 lines of body should probably be a script
  with a short skill in front of it.
- **Fragility.** Fragile sequences want low degrees of freedom — an exact script
  and an instruction not to improvise. Open-ended work wants high freedom.

## Resolving conflicts

**Judgment required + unattended trigger.** The most common real conflict.
Do not put a model in the critical path of a cron job or CI. Split it: the
deterministic core runs unattended; the judgment layer stays interactive. If the
judgment genuinely can't be removed, the honest verdict is that this shouldn't
be automated yet.

**Judgment required + must be enforced.** Enforcement wins. A model can be
persuaded, so anything load-bearing for safety goes in a hook or permission rule.
The skill can add guidance on top, but never instead.

**Prior art exists + conventions still needed.** Both are true. Use the existing
tool, and add a thin skill carrying only the conventions. Never rebuild the tool.

**Deterministic + fuzzy invocation.** The thin-wrapper shape. Script
owns the work; a near-empty skill owns intent mapping. The skill must not restate
the script's flags — that duplication is what rots.

**Cheap either way.** Prefer the shape with no permanent context cost. A shell
function costs nothing when unused; a model-invocable skill costs its description
in every session forever.

## Calibrating confidence

- **High** — a decisive signal fired and nothing contradicts it.
- **Medium** — a decisive signal fired but a weight signal pulls the other way,
  or one axis had to be assumed rather than established.
- **Close call** — no decisive signal fired, or two fired in opposite directions.

A close call is a real answer. Say what would settle it and ask, rather than
picking a side to sound decisive. Two shapes being *nearly* equal usually means
the choice doesn't matter much — say that too.
