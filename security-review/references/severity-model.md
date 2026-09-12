# Severity model

Severity is a judgment about real-world risk, not a CVSS lookup. Assign it as a function
of six factors:

| Factor | Question |
|---|---|
| Impact | If this fires, what is the worst outcome? (RCE, data loss, account takeover, DoS, info leak) |
| Exploitability | How hard is it to trigger? Preconditions, skill, reliability. |
| Exposure | Internet-facing, internal-only, or requires local access? |
| Privilege required | Unauthenticated, any authenticated user, or admin? |
| Data sensitivity | What class of data is reachable? (PII, secrets, payment, PHI, public) |
| Blast radius | One user, one tenant, or the whole environment? |

## Levels

- **Critical** — Direct, reliable path to full compromise with low privilege and high
  exposure. Unauthenticated RCE on an internet-facing service. Secret material committed to
  a public repo. Auth bypass on a primary login. Fix before deploy / rotate now.
- **High** — Serious impact but with a meaningful precondition: authenticated RCE, IDOR
  exposing other tenants' data, SSRF reaching cloud metadata, privilege escalation. Fix
  this sprint.
- **Medium** — Real weakness, limited or conditional impact: stored XSS in an admin-only
  view, missing rate limiting, over-broad IAM that is not currently exploitable, verbose
  errors leaking stack traces. Schedule it.
- **Low** — Hardening gap or defense-in-depth miss with no clear exploit path: missing
  security headers, outdated-but-unreachable dependency, weak-but-not-broken config.
- **Informational** — Not a vulnerability. Style, future-proofing, or a note for context.

## Calibration rules

- **Internal is not a free downgrade.** An internal RCE is still an RCE. Downgrade only
  when exposure genuinely limits blast radius, and say why.
- **Chain when it matters.** Two Mediums that compose into account takeover are reported as
  one High with the chain spelled out.
- **Unknowns lower confidence, not severity.** If you cannot confirm exposure, keep the
  severity honest and mark the finding Needs Validation.
- **Reserve Critical.** If everything is Critical, nothing is. Most real reviews have zero
  to two.
