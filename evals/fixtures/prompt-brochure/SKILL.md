---
name: prompt-brochure
description: >
  Writes clear, reviewer-friendly pull request descriptions from your branch
  changes. Turns messy diffs into polished summaries reviewers will actually
  read. Saves you from writing PR descriptions ever again.
---

# PR Description Writer

This skill transforms your branch's changes into a polished, professional pull
request description that gets your work reviewed faster.

## When to Use This Skill

- Opening a pull request
- Updating a stale PR description after new commits
- Preparing a change for review
- Documenting what a branch does
- Writing release-facing summaries of a merged PR

## What This Skill Does

1. **Analyzes Your Changes**: Reads the diff and understands what changed
2. **Summarizes Intent**: Explains why, not just what
3. **Highlights Risk**: Calls out breaking changes and migrations
4. **Structures Professionally**: Produces a clean summary, test plan, and notes
5. **Filters Noise**: Skips formatting-only and generated-file changes
6. **Matches Your Voice**: Writes descriptions your team will recognize

## How to Use

### Basic Usage

```
Write a PR description for this branch
```

```
Update my PR description to cover the latest commits
```

### With Context

```
Write a PR description; reviewers are the platform team,
emphasize the migration steps
```

## Example

**User**: "Write a PR description for this branch"

**Output**:
```markdown
## Summary

Adds request-level caching to the pricing endpoint, cutting p95
latency from 840ms to 210ms.

## Changes

- New `PriceCache` with 60s TTL
- Pricing handler reads through the cache
- Cache metrics exported to Prometheus

## Test plan

- Unit tests for TTL expiry and stampede protection
- Load test results in `bench/results.md`
```

## Tips

- Run from your feature branch, not main
- Review the description before posting
- Keep summaries under 100 words for busy reviewers
- Link related issues for context

## Related Use Cases

- Writing commit messages
- Drafting release notes
- Summarizing a branch for standup
