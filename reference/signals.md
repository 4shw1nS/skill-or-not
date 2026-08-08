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
| **Runs unattended** — no human or model present at runtime | script + hook/cron/CI |
| **Identical invocation every time** | alias |
| **Needs reproducibility, speed, or bulk** | script |
| **Arguments fully determined by the request** | CLI |
| **Enforcement must be unbypassable** | hook + permissions |
| **Prior art exists** | build nothing |
| **The rules are already encoded in a linter/formatter/validator** | run that tool |

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
