# Security policy

This repository vets what an agent is about to trust. A way to hide an instruction from it is exactly
the report I want.

## Reporting

Use **[Report a vulnerability](https://github.com/andreybuilt/security-skills/security/advisories/new)**
on this repository. It opens a private advisory that only the maintainer can see. Please do not open a
public issue for an evasion that is not already listed.

A useful report carries:

- a minimal file that demonstrates it, or its bytes described exactly;
- what `scan_hidden.py` reported, and what it should have reported;
- whether the shape needs `--strict` to matter.

## What counts

| Severity | Shape |
|---|---|
| Highest | Hidden or invisible content that the scanner passes as CLEAN without `--strict`: a new smuggling character, encoding or file shape. |
| High | Content in the published skills themselves that an agent would follow as an instruction it should not. |
| Normal | A WARN-tier phrase evasion, or a false positive on ordinary text. |

**Already public, no report needed:** paraphrase, split commands and homoglyphs against the phrase
groups, listed under [What this does not catch](README.md#what-this-does-not-catch).

## What happens next

This is a one-maintainer project, so responses are best effort. A confirmed evasion lands as a
malicious fixture and its benign twin first, then the fix.

## Supported versions

Only the latest release and `main` receive fixes.
