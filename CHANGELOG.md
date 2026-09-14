# Changelog

All notable changes to this project. Dates are the day the change was published.

## [1.0.0] - 2026-09-14

First tagged release. What it contains:

### Skills

- **`security-review`**: structured AppSec, cloud, Kubernetes and CI/CD review returning evidence-backed
  findings with severity and a concrete fix, mapped to OWASP, NIST SSDF, CIS and SLSA.
- **`skill-audit`**: pre-install audit of skills, plugins, MCP configs and instruction files, ending in
  a Safe to deploy / Review first / Quarantine verdict.

### Scanner

- **`skill-audit/scripts/scan_hidden.py`**: zero-dependency raw-byte scan for zero-width and
  bidirectional characters, tag smuggling, hidden HTML comments, standalone variation selectors,
  undecodable files and three phrase groups. HIGH fails by default; WARN fails under `--strict`.

### Tests

- Eight malicious fixtures, each paired with a benign twin.
- Plant-then-remove tests for a hidden zero-width character and a goal-override phrase.
- Self-scan of both published skills, and a leak sweep for identifiers.
- CI on every push and pull request, with a read-only token and a SHA-pinned checkout action.

### Fixed before this release

- The README title and clone command named a working title and a fork placeholder.
- The install commands copied from a directory that does not exist after cloning.

[1.0.0]: https://github.com/andreybuilt/security-skills/releases/tag/v1.0.0
