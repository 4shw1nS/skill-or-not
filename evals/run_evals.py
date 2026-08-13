#!/usr/bin/env python3
"""Run the blind-runnable eval cases against a live `claude` CLI and grade them.

Each case runs in a fresh headless session (`claude -p`) from an empty working
directory, so no project context leaks in and no two cases share a session.
The runner grades the mechanical half of the pass criteria automatically:

  1. fired      — did the skill-or-not skill engage at all?
  2. primary    — does the `Build:` line name `expected_primary`?
  3. forbidden  — does `Build:`/`Plus:` avoid everything in `expected_not`?
                  (`Don't build:` is allowed to name them — that's its job.)

The third criterion — the stated reason matching `decisive_signal` — needs
judgment. By default the runner prints both side by side for a human; with
--judge it asks a second, cheap model for a YES/NO and records that instead.
Treat auto-grades as a screen, not a court: anything marked MANUAL, and any
FAIL you find surprising, deserves a human read of the saved transcript.

Usage:
    python3 run_evals.py --dry-run
    python3 run_evals.py --cases resize-800,uuid-gen
    python3 run_evals.py --judge
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

CASES_FILE = Path(__file__).parent / "cases.jsonl"
SKILL_NAME = "skill-or-not"

# What each label looks like when it leads a `Build:` or `Plus:` line. Labels
# are a controlled vocabulary; free text is matched against these patterns.
LABEL_PATTERNS: dict[str, str] = {
    "cli-script": r"\b(cli|script|command-line|makefile|shell)\b|\.(sh|py)\b",
    "script": r"\b(cli|script|command-line|makefile|shell)\b|\.(sh|py)\b",
    "scripts": r"\b(cli|script|command-line|makefile|shell)\b|\.(sh|py)\b",
    "alias": r"\b(alias|shell function|one-liner|makefile)\b",
    "skill": r"\bskill\b",
    "thin-skill": r"\bskill\b",
    "user-invocable-skill": r"\bskill\b",
    "hook": r"\bhook\b",
    "permissions": r"\b(permission|deny rule)\b",
    "ci": r"\b(ci|pipeline|github actions?)\b",
    "mcp": r"\bmcp\b",
    "nothing": r"\b(nothing|prior art|already (does|exists|solved|built)|use what exists|sips|imagemagick|uuidgen|built-?in)\b",
    "scheduled-task": r"\b(schedul|cron|routine)\w*\b",
    "claude-md": r"\bclaude\.?md\b",
    "plugin": r"\bplugin\b",
    "subagent": r"\b(sub-?agents?|agents?)\b",
    "bin": r"\b(bin|binar|executable)\w*\b",
    "template": r"\btemplate\b",
    "lint-rule": r"\b(lint|rule)\w*\b",
    "extend-existing": r"\b(extend|existing|incumbent|current skill|one skill)\b",
    # As a forbidden label: a *new* skill beside an incumbent. Plain "skill"
    # would false-positive on "extend the existing skill".
    "second-skill": r"\b(second|separate|another|new)\s+(model-invocable\s+)?skill\b",
}

# Labels whose pass criteria can't be reduced to a Build-line pattern.
MANUAL_PRIMARY = {"close-call", "ask-then-conditional"}

VERDICT_KEYS = ("Build", "Plus", "Don't build", "Because", "Confidence", "Flips if")
# Verdicts arrive as plain lines, bold markdown, or bullet items ("- **Build:** x").
VERDICT_LINE = re.compile(
    r"^\s*(?:[-*+>]\s+)?\**({}):\**\s*(.*)$".format("|".join(re.escape(k) for k in VERDICT_KEYS))
)


def load_cases(only: set[str] | None, include_non_blind: bool) -> list[dict]:
    cases = [json.loads(line) for line in CASES_FILE.read_text().splitlines() if line.strip()]
    if only is not None:
        missing = only - {c["id"] for c in cases}
        if missing:
            sys.exit(f"error: unknown case id(s): {', '.join(sorted(missing))}")
        return [c for c in cases if c["id"] in only]
    if include_non_blind:
        return cases
    return [c for c in cases if c.get("blind_runnable", True)]


def run_case(case: dict, args: argparse.Namespace, workdir: Path) -> dict:
    """One fresh headless session; returns raw events plus the final text."""
    cmd = [args.claude_bin, "-p", case["input"], "--output-format", "stream-json", "--verbose"]
    if args.model:
        cmd += ["--model", args.model]
    for extra in args.claude_arg or []:
        cmd += extra.split(" ", 1) if " " in extra else [extra]

    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, cwd=workdir, capture_output=True, text=True, timeout=args.timeout
        )
    except subprocess.TimeoutExpired:
        return {"error": f"timed out after {args.timeout}s", "events": [], "result_text": ""}
    except OSError as exc:
        return {"error": f"could not run {args.claude_bin}: {exc}", "events": [], "result_text": ""}

    events = []
    for line in proc.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    result_text = ""
    for event in events:
        if event.get("type") == "result":
            result_text = event.get("result") or ""

    error = None
    if proc.returncode != 0 and not result_text:
        error = f"claude exited {proc.returncode}: {proc.stderr.strip()[:500]}"

    return {
        "error": error,
        "events": events,
        "result_text": result_text,
        "seconds": round(time.monotonic() - started, 1),
    }


def skill_fired(events: list[dict]) -> bool:
    """True if any tool_use in the transcript invoked the skill-or-not skill."""
    for event in events:
        message = event.get("message") or {}
        for block in message.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                if SKILL_NAME in json.dumps(block.get("input", {})) + str(block.get("name", "")):
                    return True
    return False


def parse_verdict(text: str) -> dict[str, str]:
    """Collect the labeled verdict lines, folding continuation lines in."""
    verdict: dict[str, str] = {}
    current: str | None = None
    for line in text.splitlines():
        match = VERDICT_LINE.match(line)
        if match:
            current = match.group(1)
            verdict[current] = match.group(2).strip()
        elif current and line.startswith((" ", "\t")) and line.strip():
            verdict[current] += " " + line.strip()
        else:
            current = None
    return verdict


def matches(label: str, text: str) -> bool | None:
    """None means this label has no pattern and needs a human."""
    pattern = LABEL_PATTERNS.get(label)
    if pattern is None:
        return None
    return re.search(pattern, text, re.IGNORECASE) is not None


def check_forbidden(
    label: str, verdict: dict[str, str], full_text: str, build_only: bool = False
) -> bool | None:
    """True = the forbidden shape was recommended. None = needs a human.

    build_only restricts the scan to the Build line — used when the same
    pattern is expected in the composition, so its presence in Plus is a pass,
    not a hit (e.g. expected_not "cli-script" with expected_composition
    "script" forbids a script *leading* the verdict, not appearing in it).
    """
    build = verdict.get("Build", "")
    build_plus = build if build_only else build + " " + verdict.get("Plus", "")
    if label == "fat-skill":
        # A thin skill in Plus is the approved composition; a skill leading
        # the verdict is the failure.
        return matches("skill", build)
    if label == "skill-only":
        return bool(matches("skill", build)) and "nothing else" in build_plus.lower()
    if label == "model-invocable-skill":
        # Recommending a skill is fine only alongside the invocation control.
        if not matches("skill", build_plus):
            return False
        return not re.search(r"disable-model-invocation|user-invocable", full_text, re.I)
    return matches(label, build_plus)


def judge_reason(case: dict, verdict: dict[str, str], args: argparse.Namespace) -> bool | None:
    """Ask a cheap model whether the stated reason matches the expected signal."""
    because = verdict.get("Because", "")
    if not because:
        return None
    prompt = (
        "You are grading one eval case for a decision rubric that runs a prior-art "
        "check (Step 0) then gates G0-G8: G0 actor, G1 enforcement, G2 judgment, "
        "G3 fact-vs-procedure, G4 trigger, G5 reach, G6 context/isolation, "
        "G7 distribution, G8 invocation settings.\n\n"
        f"Expected decisive signal: {case['decisive_signal']}\n"
        f"The verdict's stated reason: {because}\n\n"
        "Do these name the same terminating reason? Gate numbers and signal prose "
        "are interchangeable — \"enforcement must be unbypassable\" IS G1, \"prior "
        "art\" IS Step 0, \"no decision between request and command\" IS G2. A "
        "reason that names the expected signal plus a secondary supporting one "
        "still matches; a reason that replaces it with a different signal does "
        "not. Answer with exactly one word: YES or NO."
    )
    try:
        proc = subprocess.run(
            [args.claude_bin, "-p", prompt, "--model", args.judge_model, "--output-format", "json"],
            capture_output=True, text=True, timeout=120,
        )
        answer = json.loads(proc.stdout).get("result", "")
    except (subprocess.SubprocessError, OSError, json.JSONDecodeError):
        return None
    answer = answer.strip().upper()
    if answer.startswith("YES"):
        return True
    if answer.startswith("NO"):
        return False
    return None


def grade(case: dict, run: dict, args: argparse.Namespace) -> dict:
    if run.get("error"):
        return {"id": case["id"], "overall": "ERROR", "error": run["error"]}

    text = run["result_text"]
    verdict = parse_verdict(text)
    fired = skill_fired(run["events"])
    result: dict = {
        "id": case["id"],
        "fired": fired,
        "verdict": verdict,
        "seconds": run.get("seconds"),
    }

    expected = case["expected_primary"]
    if expected in MANUAL_PRIMARY:
        # A single -p turn can't answer the clarifying question these cases
        # exist to provoke, so nothing here is auto-gradable — not even the
        # reason. Record a hedge heuristic and hand the transcript to a human.
        result["primary_ok"] = None
        result["hedge_detected"] = "close call" in text.lower() or "?" in text
        result["reason_ok"] = None
        result["expected_signal"] = case["decisive_signal"]
        result["because"] = verdict.get("Because", "")
        result["forbidden_hits"] = {}
        result["overall"] = "MANUAL" if fired else "NO-FIRE"
        return result
    result["primary_ok"] = matches(expected, verdict.get("Build", ""))

    composition_patterns = {
        LABEL_PATTERNS.get(c) for c in case.get("expected_composition", [])
    } - {None}
    forbidden_hits = {}
    for label in case.get("expected_not", []):
        build_only = LABEL_PATTERNS.get(label) in composition_patterns
        forbidden_hits[label] = check_forbidden(label, verdict, text, build_only)
    result["forbidden_hits"] = forbidden_hits

    result["reason_ok"] = judge_reason(case, verdict, args) if args.judge else None
    result["expected_signal"] = case["decisive_signal"]
    result["because"] = verdict.get("Because", "")

    checks = [result["primary_ok"]] + [
        None if hit is None else not hit for hit in forbidden_hits.values()
    ]
    if args.judge:
        checks.append(result["reason_ok"])
    if not fired:
        result["overall"] = "NO-FIRE"
    elif any(c is False for c in checks):
        result["overall"] = "FAIL"
    elif any(c is None for c in checks):
        result["overall"] = "MANUAL"
    else:
        result["overall"] = "PASS"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cases", help="Comma-separated case ids to run (default: all blind-runnable)")
    parser.add_argument("--model", help="Model for the session under test (default: CLI default)")
    parser.add_argument("--include-non-blind", action="store_true",
                        help="Also run cases marked blind_runnable: false")
    parser.add_argument("--dry-run", action="store_true", help="Print what would run, run nothing")
    parser.add_argument("--judge", action="store_true",
                        help="Grade the Because: line with a second model call")
    parser.add_argument("--judge-model", default="opus", help="Model for --judge (default: opus)")
    parser.add_argument("--outdir", type=Path,
                        help="Where to write results.json and per-case transcripts "
                             "(default: results/<UTC timestamp>)")
    parser.add_argument("--claude-bin", default="claude", help="Path to the claude CLI")
    parser.add_argument("--claude-arg", action="append",
                        help="Extra argument passed through to the claude CLI; repeatable")
    parser.add_argument("--timeout", type=int, default=600, help="Per-case timeout in seconds")
    parser.add_argument("--regrade", type=Path, metavar="DIR",
                        help="Re-grade saved transcripts from a previous run's output directory "
                             "instead of launching sessions — grader and label changes shouldn't "
                             "cost fresh sessions")
    args = parser.parse_args()

    only = set(args.cases.split(",")) if args.cases else None
    cases = load_cases(only, args.include_non_blind or args.regrade is not None)

    if args.dry_run:
        for case in cases:
            print(f"{case['id']:<24} expected: {case['expected_primary']}")
        print(f"\n{len(cases)} case(s) would run, one fresh `claude -p` session each.")
        return 0

    if args.regrade:
        results = []
        for case in cases:
            saved = args.regrade / f"{case['id']}.json"
            if not saved.is_file():
                continue
            results.append(grade(case, json.loads(saved.read_text()), args))
        if not results:
            sys.exit(f"error: no saved transcripts in {args.regrade}")
        outdir = args.outdir or args.regrade
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "results-regraded.json").write_text(json.dumps(results, indent=2))
    else:
        outdir = args.outdir or Path(__file__).parent / "results" / datetime.now(
            timezone.utc
        ).strftime("%Y%m%dT%H%M%SZ")
        outdir.mkdir(parents=True, exist_ok=True)
        results = []
        for case in cases:
            print(f"running {case['id']} ...", flush=True)
            with tempfile.TemporaryDirectory(prefix="skill-or-not-eval-") as workdir:
                run = run_case(case, args, Path(workdir))
            (outdir / f"{case['id']}.json").write_text(json.dumps(run, indent=2))
            results.append(grade(case, run, args))
        (outdir / "results.json").write_text(json.dumps(results, indent=2))

    tally: dict[str, int] = {}
    print(f"\n{'case':<24} {'fired':<6} {'primary':<8} {'forbidden':<10} {'reason':<7} overall")
    print("-" * 70)
    for r in results:
        tally[r["overall"]] = tally.get(r["overall"], 0) + 1
        if r["overall"] == "ERROR":
            print(f"{r['id']:<24} {'-':<6} {'-':<8} {'-':<10} {'-':<7} ERROR  {r['error']}")
            continue
        fmt = lambda v: "-" if v is None else ("ok" if v else "BAD")
        forbidden = "clear" if not r["forbidden_hits"] else (
            "HIT" if any(r["forbidden_hits"].values())
            else ("-" if any(v is None for v in r["forbidden_hits"].values()) else "clear")
        )
        print(f"{r['id']:<24} {str(r['fired']).lower():<6} {fmt(r['primary_ok']):<8} "
              f"{forbidden:<10} {fmt(r['reason_ok']):<7} {r['overall']}")

    print(f"\n{'  '.join(f'{k}: {v}' for k, v in sorted(tally.items()))}")
    print(f"transcripts and results.json in {outdir}")
    print("MANUAL rows and surprising FAILs deserve a human read of the transcript.")
    return 1 if any(r["overall"] in ("FAIL", "ERROR", "NO-FIRE") for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
