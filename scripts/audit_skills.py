#!/usr/bin/env python3
"""Measure structural facts about one skill or a directory of skills.

This script deliberately does no judging. It counts, parses, and detects drift;
deciding what the numbers mean is the model's job. That split is the same one
the skill recommends to others, applied to itself.

Usage:
    python3 audit_skills.py <path>              # one skill dir, or a dir of them
    python3 audit_skills.py <path> --format json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Limits published in the Agent Skills docs. Exceeding them is a real defect,
# not a style preference, so they are checked rather than advised.
NAME_MAX_CHARS = 64
DESCRIPTION_MAX_CHARS = 1024
BODY_MAX_LINES = 500

# Reserved words the docs prohibit in a skill's `name` field.
RESERVED_NAME_WORDS = ("anthropic", "claude")

# A skill body is pinned in context for the rest of the session once loaded, so
# length past this point is worth flagging well before the hard 500-line cap.
BODY_ADVISORY_LINES = 200

# Vendored and generated trees. Their scripts are not the skill's interface, and
# their bundled markdown would otherwise count as "documentation", hiding drift.
EXCLUDED_DIRS = frozenset({
    ".venv", "venv", "env", "site-packages", "node_modules",
    ".git", "__pycache__", ".pytest_cache", "build", "dist", ".tox", ".mypy_cache",
})


def is_vendored(path: Path, root: Path) -> bool:
    """True if any path segment below `root` is a vendored or generated directory."""
    return any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts)

NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# Matches the first flag string in an argparse add_argument call.
ARGPARSE_FLAG_PATTERN = re.compile(r"""add_argument\(\s*["'](-{1,2}[a-zA-Z][\w-]*)["']""")
# First-person openings the docs warn break skill discovery.
FIRST_PERSON_PATTERN = re.compile(r"^\s*(I |I'|You can |You should |We )", re.IGNORECASE)


def parse_frontmatter(text: str) -> tuple[dict[str, str], int]:
    """Return (fields, body_line_count). Handles YAML block scalars (`>` and `|`).

    Only the flat top-level string fields a skill uses are parsed; this avoids a
    PyYAML dependency so the script runs anywhere python3 does.
    """
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}, len(text.splitlines())

    fields: dict[str, str] = {}
    current_key: str | None = None
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        # A continuation line of a block scalar is indented; a new key is not.
        if line[0].isspace() and current_key:
            fields[current_key] = (fields[current_key] + " " + line.strip()).strip()
            continue
        key, sep, value = line.partition(":")
        if not sep:
            continue
        current_key = key.strip()
        value = value.strip()
        fields[current_key] = "" if value in (">", "|", ">-", "|-") else value

    body = text[match.end():]
    return fields, len(body.splitlines())


def documented_flags(skill_dir: Path) -> set[str]:
    """Every flag mentioned in any markdown file in the skill."""
    mentioned: set[str] = set()
    for md in skill_dir.rglob("*.md"):
        if is_vendored(md, skill_dir):
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        mentioned.update(re.findall(r"-{1,2}[a-zA-Z][\w-]*", text))
    return mentioned


def script_flags(skill_dir: Path) -> dict[str, list[str]]:
    """Flags each Python script accepts, per file."""
    found: dict[str, list[str]] = {}
    for script in skill_dir.rglob("*.py"):
        if is_vendored(script, skill_dir):
            continue
        try:
            source = script.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        flags = sorted(set(ARGPARSE_FLAG_PATTERN.findall(source)))
        if flags:
            found[str(script.relative_to(skill_dir))] = flags
    return found


def git_dirty(skill_dir: Path) -> bool | None:
    """True if the skill has uncommitted changes. None if not tracked by git."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", str(skill_dir)],
            cwd=skill_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return bool(result.stdout.strip())


def audit_one(skill_dir: Path) -> dict:
    """Collect every measurable fact about a single skill directory."""
    skill_md = skill_dir / "SKILL.md"
    report: dict = {"path": str(skill_dir), "name_from_dir": skill_dir.name, "problems": []}

    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        report["problems"].append("no SKILL.md — not a skill directory")
        return report
    except OSError as exc:
        report["problems"].append(f"could not read SKILL.md: {exc}")
        return report

    fields, body_lines = parse_frontmatter(text)
    name = fields.get("name", "")
    description = fields.get("description", "")

    report.update(
        {
            "name": name or None,
            "body_lines": body_lines,
            "description_chars": len(description),
            "invocation": {
                "disable_model_invocation": fields.get("disable-model-invocation") == "true",
                "user_invocable": fields.get("user-invocable") != "false",
                "context_fork": fields.get("context") == "fork",
            },
            "has_scripts": any(
                not is_vendored(p, skill_dir)
                for pattern in ("*.py", "*.sh")
                for p in skill_dir.rglob(pattern)
            ),
            "reference_files": sorted(
                str(p.relative_to(skill_dir))
                for p in skill_dir.rglob("*.md")
                if p.name != "SKILL.md" and not is_vendored(p, skill_dir)
            ),
            "git_dirty": git_dirty(skill_dir),
        }
    )

    # Frontmatter validity, per the published limits.
    if not name:
        report["problems"].append("missing `name`")
    else:
        if len(name) > NAME_MAX_CHARS:
            report["problems"].append(f"name exceeds {NAME_MAX_CHARS} chars")
        if not NAME_PATTERN.match(name):
            report["problems"].append("name must be lowercase letters, numbers, hyphens only")
        if any(word in name.lower() for word in RESERVED_NAME_WORDS):
            report["problems"].append(f"name contains a reserved word {RESERVED_NAME_WORDS}")
        if name != skill_dir.name:
            report["problems"].append(f"name `{name}` does not match directory `{skill_dir.name}`")

    if not description:
        report["problems"].append("missing `description` — the skill cannot be discovered")
    else:
        if len(description) > DESCRIPTION_MAX_CHARS:
            report["problems"].append(f"description exceeds {DESCRIPTION_MAX_CHARS} chars")
        if FIRST_PERSON_PATTERN.match(description):
            report["problems"].append("description is not third person")
        if "use when" not in description.lower() and "triggers on" not in description.lower():
            report["problems"].append("description states what but not when — hurts discovery")

    # Context budget.
    if body_lines > BODY_MAX_LINES:
        report["problems"].append(
            f"body is {body_lines} lines, over the {BODY_MAX_LINES}-line cap — split it"
        )
    elif body_lines > BODY_ADVISORY_LINES:
        report["problems"].append(
            f"body is {body_lines} lines; it stays in context all session once loaded"
        )

    # Documentation drift: flags the code accepts but no markdown mentions.
    documented = documented_flags(skill_dir)
    drift: dict[str, list[str]] = {}
    for script, flags in script_flags(skill_dir).items():
        undocumented = [f for f in flags if f not in documented]
        if undocumented:
            drift[script] = undocumented
    report["undocumented_flags"] = drift
    if drift:
        total = sum(len(v) for v in drift.values())
        report["problems"].append(f"{total} script flag(s) undocumented in any markdown")

    if report["git_dirty"]:
        report["problems"].append("uncommitted changes — published copy may not match local")

    return report


def find_skills(path: Path) -> list[Path]:
    """A skill dir has a SKILL.md; otherwise treat the path as a container."""
    if (path / "SKILL.md").is_file():
        return [path]
    return sorted(child for child in path.iterdir() if (child / "SKILL.md").is_file())


def print_table(reports: list[dict]) -> None:
    header = f"{'skill':<26} {'body':>6}  {'scripts':<8} {'problems'}"
    print(header)
    print("-" * len(header))
    for r in reports:
        name = r.get("name") or r["name_from_dir"]
        body = r.get("body_lines", 0)
        scripts = "yes" if r.get("has_scripts") else "no"
        count = len(r["problems"])
        flag = "clean" if count == 0 else f"{count} issue{'s' if count != 1 else ''}"
        print(f"{name:<26} {body:>6}  {scripts:<8} {flag}")
    print()
    for r in reports:
        if r["problems"]:
            print(f"{r.get('name') or r['name_from_dir']}:")
            for problem in r["problems"]:
                print(f"  - {problem}")
            print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", type=Path, help="A skill directory, or a directory of skills")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                        help="Output format (default: table)")
    args = parser.parse_args()

    if not args.path.is_dir():
        print(f"error: not a directory: {args.path}", file=sys.stderr)
        return 2
    # Resolve so relative paths like "." still yield a real directory name to
    # compare against the skill's `name` field.
    args.path = args.path.resolve()

    skills = find_skills(args.path)
    if not skills:
        print(f"error: no SKILL.md found in {args.path} or its immediate children", file=sys.stderr)
        return 1

    reports = [audit_one(s) for s in skills]

    if args.format == "json":
        print(json.dumps(reports, indent=2))
    else:
        print_table(reports)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
