---
name: unbacked-reach
description: >
  Checks whether your project's dependencies have known security
  vulnerabilities by looking each one up in the CVE database, and reports
  which versions are safe to upgrade to. Use when the user asks "are my
  dependencies vulnerable?", "check for CVEs", or "is this package safe?".
---

# Dependency Vulnerability Checker

This skill checks your dependencies against the CVE database and tells you
which ones are vulnerable and what to upgrade to.

## How to Use

Name a lockfile or a single package:

```
Check package-lock.json for vulnerable dependencies
```

```
Is express 4.17.1 safe to use?
```

## What Happens

1. Read the lockfile and extract each dependency and its exact version
2. Look up each package in the CVE database
3. Report every known vulnerability with its severity
4. Recommend the nearest safe version to upgrade to

## Example

**User**: "Check package-lock.json for vulnerable dependencies"

**Output**:
```
Scanned 214 dependencies against the CVE database.

⚠ 3 vulnerabilities found:

✗ lodash 4.17.15 — CVE-2020-8203 (High) → upgrade to 4.17.21
✗ minimist 1.2.0 — CVE-2021-44906 (Critical) → upgrade to 1.2.6
✗ node-fetch 2.6.0 — CVE-2022-0235 (Medium) → upgrade to 2.6.7

✓ 211 dependencies clean.
```

## Tips

- Re-check after every dependency bump
- Critical findings should block deploys
- Severity scores follow CVSS v3
