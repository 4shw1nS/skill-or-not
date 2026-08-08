# Shapes

Every shape a candidate can take, what it actually costs, and the signal that
decides it. Shapes on different axes compose; shapes on the same axis compete.

## Contents

- [Axis: build nothing](#axis-build-nothing)
- [Axis: deterministic code](#axis-deterministic-code) — alias, script, library
- [Axis: model in the loop](#axis-model-in-the-loop) — skill, subagent, CLAUDE.md
- [Axis: trigger](#axis-trigger) — hook, scheduled task, CI
- [Axis: reach](#axis-reach) — MCP server
- [Axis: distribution](#axis-distribution) — personal, plugin, marketplace
- [What competes with what](#what-competes-with-what)

---

## Axis: build nothing

### Use what exists
**Cost:** none. **Decisive for:** a standard tool already does this (`sips`,
ImageMagick, `jq`, `gh`, a built-in command, an installed skill). **Decisive
against:** nothing does it, or the existing tool needs conventions it can't know.

Always the first hypothesis. The most expensive mistake in this whole space is
building a wrapper around something already solved.

### Just ask Claude
**Cost:** none. **Decisive for:** you do this rarely, and phrasing it takes less
effort than remembering a tool exists. **Decisive against:** you have repeated
the same instructions three or more times.

Repetition is the threshold. Below it, formalizing costs more than it saves.

---

## Axis: deterministic code

### Shell alias / function / Makefile target
**Cost:** one line in a dotfile. **Decisive for:** the invocation is identical
every time. **Decisive against:** arguments vary in ways that need interpretation.

### CLI script
**Cost:** a file to maintain, plus documentation that will drift from it.
**Decisive for:** the procedure is closed-form; the same inputs must always give
the same outputs; it needs to run without a model, fast, or in bulk.
**Decisive against:** the interesting part is deciding *what* to run.

The default shape for anything mechanical. Cheap to test, cheap to reason about,
free of context cost. When in doubt between this and a skill, this wins — the
gate order exists to enforce that.

### Library / package
**Cost:** versioning, an API surface, real maintenance.
**Decisive for:** other code, not other people, is the consumer.

---

## Axis: model in the loop

### Skill — model-invocable (default)
**Cost:** its `description` occupies the system prompt in **every session**,
whether used or not. Its body enters the conversation on invocation and **stays
for the rest of the session**.
**Decisive for:** Claude should notice this is relevant without being told;
the procedure requires reading ambient context before deciding.
**Decisive against:** the user always knows when they want it — then make it
user-invocable and stop paying the description cost.

### Skill — user-invocable only (`disable-model-invocation: true`)
**Cost:** none until invoked. The description is *not* loaded at startup.
**Decisive for:** side effects, irreversibility, or timing the user must control
— deploys, commits, sends, posts.
**Decisive against:** the whole value is Claude noticing unprompted.

The cheapest skill shape. If you're unsure whether a skill is worth its context,
this is the version that costs nothing until used.

### Skill — model-only (`user-invocable: false`)
**Cost:** description always in context. **Decisive for:** background knowledge
that isn't an action a user would ever invoke — how a legacy system behaves,
domain constraints Claude should apply when relevant.

### Skill with `context: fork`
**Cost:** as above, plus a subagent round trip.
**Decisive for:** the work produces heavy intermediate output that would crowd
the main thread, but the *instructions* live with the skill.

### Subagent
**Cost:** a cold start with no conversation context, plus delegation overhead.
**Decisive for:** parallel fan-out, or isolating a large search whose transcript
you don't want. **Decisive against:** the task needs what's already in context —
the subagent starts cold and must re-derive it.

Choose subagents for context hygiene and parallelism, never for capability.

### CLAUDE.md entry
**Cost:** loaded on **every** turn of every session in that project.
**Decisive for:** facts that are always true — conventions, architecture, rules.
**Decisive against:** procedures invoked occasionally. Once a CLAUDE.md section
turns into steps, it has become a skill and should move.

---

## Axis: trigger

### Hook
**Cost:** a config entry; runs on a lifecycle event whether or not you want it.
**Decisive for:** the trigger is a tool or file event, and the response is
identical every time; or enforcement must be unbypassable.
**Decisive against:** the response requires judgment.

Enforcement is the key word. A skill that says "never do X" is a suggestion the
model may not follow; a `PreToolUse` hook is a wall. Never answer a safety
requirement with instructions.

### Scheduled task / cron
**Cost:** runs unattended, so failures are silent unless you build alerting.
**Decisive for:** a clock is the trigger.
**Decisive against:** nothing — but the *critical path* must not depend on model
judgment. Schedule the deterministic part; keep the judgment interactive.

### CI job
**Cost:** pipeline time. **Decisive for:** it must run on every push,
reproducibly, with an auditable record. **Decisive against:** any model in the
critical path, since CI needs determinism.

---

## Axis: reach

### MCP server
**Cost:** a running process, credentials to manage, tool definitions in context.
**Decisive for:** Claude needs authenticated access to an external system, and
that access is reusable across many different tasks.
**Decisive against:** one single-purpose call — a script holding the credential
is simpler.

Reach is not knowledge. MCP grants access; it cannot teach conventions. When a
task needs both, the answer is MCP **plus** a skill, and neither alone is enough.

---

## Axis: distribution

### Personal `~/.claude/` or `~/bin`
**Cost:** none. **Decisive for:** one user, one machine, fast iteration.

### Plugin
**Cost:** a manifest, a version, namespaced invocation (`/plugin-name:skill`).
**Decisive for:** teammates, several repos, or versioned releases. Bundles
skills, agents, hooks, MCP config, and `bin/` executables together.
**Decisive against:** you are the only user.

Packaging is an **independent axis**. "Skill or plugin?" is a category error —
a plugin is how a skill (or a hook, or a binary) travels. Start standalone,
convert when you need to share.

### Marketplace
**Cost:** review, and a public contract you now maintain.
**Decisive for:** strangers should find it.

---

## What competes with what

Within an axis, pick one. Across axes, compose.

| Competing (pick one) | Composing (expect several) |
|---|---|
| alias vs script vs library | script + skill |
| model-invocable vs user-invocable | MCP + skill |
| main thread vs subagent | script + hook + CI |
| CLAUDE.md vs skill | schedule + script + skill |
| personal vs plugin | plugin wrapping skill + hook + bin |

A verdict naming only one shape is usually incomplete. A verdict naming two on
the same axis is incoherent.
