# Attack vector catalog

Documented, real-world cases where a text-only AI instruction file acted as an attack
payload. These are the signatures `skill-audit` matches against. A `.md`, `.mdc`, or
`.cursorrules` file opens in any editor and passes virus scans, but in an AI-integrated
environment it is operational code.

| # | Attack | Surface | Disclosed | What it did |
|---|---|---|---|---|
| 1 | **CamoLeak** | GitHub Copilot Chat | Jun 2025, CVSS 9.6 (Legit Security) | Hidden HTML comment in a PR silently exfiltrated private source code, API keys, and undisclosed vuln details. No malware, no phishing. Fixed by disabling image rendering in Copilot Chat. |
| 2 | **RoguePilot** | GitHub Codespaces | Feb 2026 (Orca Security) | Malicious GitHub Issue triggered passive prompt injection when a developer launched a Codespace, exfiltrating `GITHUB_TOKEN` and enabling full repo takeover. |
| 3 | **Kilo Code** | VS Code extension | CVE-2025-11445, Sep 2025 | A malicious prompt in any ingested file (README, issue, website) manipulated the agent into whitelisting `git add`, `commit`, `push` in `settings.json` — automated supply-chain poisoning. Patched v4.88.0. |
| 4 | **AGENTS.md / CLAUDE.md goal hijack** | VS Code agents | Dec 2025 (Prompt Security) | VS Code auto-injects `AGENTS.md` into every chat request and treats it as instructions, not docs. A malicious `AGENTS.md` quietly convinced the agent to email internal org data out during normal coding. |
| 5 | **Rules File Backdoor** | Cursor & GitHub Copilot | 2025 (Pillar Security) | `.cursorrules` / `.mdc` weaponized with hidden Unicode (zero-width joiners, bidirectional markers) — invisible to humans, fully readable by AI. A poisoned file in a cloned repo silently makes Cursor insert malicious code into every file it generates, team-wide. |
| 6 | **CurXecute** | Cursor RCE via MCP | CVE-2025-54135, CVSS 8.6, Jul 2025 (Aim Labs) | A poisoned prompt via an MCP server (e.g. Slack) silently rewrites `~/.cursor/mcp.json` and executes attacker-controlled commands under developer privileges. No interaction required. Fixed Cursor v1.3. |

## Blast radius (what a compromised instruction file can reach)

- **Data exfiltration** — extract source, API keys, vuln details (CamoLeak).
- **Code execution** — rewrite settings to authorize git/commands, turning text into
  workflow control (Kilo Code).
- **System compromise** — steal session tokens, full repo/host takeover (RoguePilot).
- **AI manipulation** — override the agent's goals for a session, biasing reviews,
  approvals, and security decisions (AGENTS.md / CLAUDE.md).

## The one rule

**Treat every external document or file as a potential attack vector requiring explicit
validation before AI processing.** Traditional scanners look for malicious *code*; these
attacks carry malicious *instructions*. Different detector, different discipline.

## Mapping signatures to detection categories

| Attack | Primary signal to look for | Detection category |
|---|---|---|
| CamoLeak | Hidden HTML comments; image-render/exfil instructions | Hidden content; Exfiltration |
| RoguePilot | Instructions reading tokens/env on ingest | Credential access |
| Kilo Code | Instructions that edit `settings.json` / whitelist commands | Settings tampering |
| AGENTS/CLAUDE.md | Goal-override, "email/send out", "treat as instructions" | Injected instructions; Exfiltration |
| Rules File Backdoor | Zero-width / bidi / invisible Unicode | Hidden content |
| CurXecute | `mcp.json` rewrite; MCP `command` execution | Settings tampering; RCE |
