# MCP, connector & plugin checklist

For MCP servers, connectors, and plugins, the instruction-file risks still apply, plus
capability risks unique to executable integrations. CurXecute (CVE-2025-54135) is the
worked example: a poisoned prompt rewrote `~/.cursor/mcp.json` and ran commands.

## MCP server config
- **`command` / `args`** — what binary launches? Is it a known tool or an arbitrary script?
  Does it `curl|bash`, run an interpreter on remote code, or point at an unvetted path?
- **`env`** — does it pull in secrets/tokens? Are credentials hardcoded in the config?
- **`url` (remote MCP)** — is the endpoint trusted and named? HTTPS? Could it serve
  attacker-controlled tool definitions or prompts?
- **Tool surface** — what tools does the server expose? Shell, filesystem write, network
  fetch, send-message? Is that scope justified by the stated purpose?
- **Config-rewrite risk** — does anything modify `mcp.json`, `settings.json`, or add servers
  silently? (CurXecute signature.)
- **Prompt-injection path** — can untrusted content flowing through the server (a Slack
  message, an issue, a webhook) reach the agent as instructions?

## Plugin manifest (`plugin.json`) and bundle
- Declared `commands`, `agents`, `hooks` — does each match the stated function?
- **Hooks** — PreToolUse/PostToolUse/Stop hooks can intercept, alter, or exfiltrate tool
  calls and outputs. Read every hook script in full.
- Bundled scripts — apply the code-execution and credential-access checks from
  `detection-checklist.md`.
- Auto-load / trigger breadth — does the description trigger it far beyond its purpose?

## Connectors / shared workflows
- What scopes/permissions does the connector request? Least privilege?
- Where does data flow? Any external sink (analytics, webhook, third-party API)?
- Is the connector from the vendor it claims, at a pinned version?

## Capability verdict guidance
- MCP/plugin that can execute commands or rewrite config, from an untrusted source =
  **Quarantine**.
- Powerful-but-plausible tool surface with no shown malicious intent = **Review first**:
  scope it down, pin it, and prefer sandboxed/least-privilege deployment.
- If you cannot read the server binary or a compiled component, you **cannot clear it** —
  say so.

## Deploying more safely (recommendations to include in the report)
- Pin versions; do not track mutable tags.
- Run MCP servers with least-privilege credentials and scoped tokens (not admin).
- Keep human-in-the-loop confirmation on; do not let an integration disable prompts.
- Re-audit on every version bump — a clean v1 does not clear v2.
