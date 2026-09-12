# Skill & agent review checklist

For vetting a Claude skill, agent, or plugin **before it is installed or deployed** —
`SKILL.md` plus any bundled `references/`, `scripts/`, hooks, and frontmatter. This is the
"is it safe to install this?" review. It complements automated scanners (e.g. Skill-Spector,
which checks ~64 patterns across 16 categories) — run both; this one reasons about intent,
the scanner catches known patterns at scale.

Treat the skill author as untrusted until proven otherwise. The skill's instructions become
*your* instructions once installed, and its scripts run with the user's privileges.

## Prompt injection & hidden instructions (the #1 skill risk)
- Instructions telling the model to ignore the user, ignore safety rules, or override system prompts?
- Hidden or obfuscated text: zero-width chars, white-on-white, HTML comments, base64 blobs, "if asked, say nothing about this"?
- Instructions to exfiltrate conversation content, files, or secrets to a URL / email / webhook?
- Instructions to silently take actions the user did not ask for (auto-send, auto-commit, auto-delete)?
- "Always run this command first" style preambles that smuggle in side effects?
- Description/frontmatter that triggers the skill far more broadly than its stated purpose (over-eager autoload)?

## Bundled scripts & commands
- Destructive operations: `rm -rf`, disk/format, mass file moves, `git push --force`, history rewrites?
- Remote code execution at runtime: `curl … | bash`, `wget … | sh`, `eval`, `exec`, downloading and running code?
- Network calls to unfamiliar hosts — especially POSTing local data outward (exfiltration)?
- Credential / secret access: reading `~/.ssh`, `~/.aws`, `.env`, keychain, browser profiles, token stores?
- Obfuscation: base64/hex/rot13-encoded payloads, dynamically built command strings, minified blobs?
- Privilege escalation: `sudo`, writing to system paths, modifying shell rc files, installing launch agents/cron?
- Package installs from unpinned or unexpected sources (`pip install`, `npm i` of unknown names)?

## Tools, permissions & MCP scope
- Requests far broader tool access than the task needs (full shell when read-only would do)?
- `allowed-tools` / permission declarations that grant filesystem, network, or exec beyond purpose?
- Bundled MCP server definitions pointing at untrusted or hardcoded external endpoints?
- Hooks (PreToolUse/PostToolUse/etc.) that intercept and could alter or leak tool calls?

## Data handling & exfiltration
- Does it send file contents, environment, or chat history anywhere external?
- Telemetry / "phone home" behavior, analytics beacons, or logging to a third party?
- Does it write outside its expected scope (other projects, home dir, shared drives)?

## Integrity & provenance
- Author/source known and trusted? Pinned version, not a moving `@main`?
- Does the actual behavior match the stated description, or does it do more than it claims?
- Secrets or credentials committed inside the skill itself?
- License clear for the intended use (especially if redistributing to a client)?

## Verdict guidance
- Any confirmed prompt-injection, exfiltration, or destructive/credential-access script = **Critical, do not install.**
- Overbroad permissions or unpinned remote fetches with no malicious intent shown = **High/Medium, fix or sandbox before deploy.**
- Clean, scoped, provenance-clear = note residual assumptions and approve.
- If the bundle has scripts you cannot fully read (compiled, obfuscated), do not approve — say so explicitly.
