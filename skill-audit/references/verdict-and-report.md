# Verdict and report

## Verdict scale
- **SAFE TO DEPLOY** — clean scan, intent matches description, scoped permissions, trusted
  pinned provenance. Note residual assumptions.
- **REVIEW FIRST** — risky capability, no shown malicious intent. Fix/scope/sandbox, then
  re-audit.
- **QUARANTINE** — confirmed hidden instruction, exfiltration, credential access, config
  rewrite, or RCE. Do not deploy. One confirmed item is enough.
- **CANNOT CLEAR** — part of the bundle is unreadable (obfuscated/compiled). Unread is not
  safe.

## Single-artifact format
```
Skill Audit — <artifact name / path>
Verdict: SAFE TO DEPLOY / REVIEW FIRST / QUARANTINE / CANNOT CLEAR
Type: skill / plugin / MCP / instruction file / prompt / brainstorm
Source & trust: <where it came from; trusted?>
Hidden-content scan: clean / N flags  (scanner output summary)

Findings:
- [Category] <title> — Confirmed/Suspected
  Evidence: <exact string/line, rendered safe>
  Risk: <what it could do; map to attack class, e.g. "Rules File Backdoor pattern">
  Action: <remove / reject / scope / pin>

Could not inspect: <files/components not readable>
Recommendation: <one line>
```

## Bundle / multi-file format
```
Skill Audit Summary — <bundle name>
Overall verdict: SAFE TO DEPLOY / REVIEW FIRST / QUARANTINE / CANNOT CLEAR
Files audited: <n>   Hidden-content flags: <n>   Confirmed findings: <n>

Per artifact:
- <file> — <verdict> — <one-line reason>
- <file> — <verdict> — <one-line reason>

Top reasons (if not Safe):
1. <finding> — <attack class> — <severity>

Not inspected: <list>
Next actions: <ordered>
```

## Reporting rules
- Lead with the verdict. The reader wants the go/no-go first.
- Quote evidence exactly, rendered safe (show `<U+200B>` etc.), so a human can verify.
- Map each real finding to a documented attack class from `attack-vector-catalog.md` for
  credibility and a path to the source.
- Always include "Could not inspect / Not reviewed." Silence reads as "all clear" when it
  is not.
- Recommend complementary automated scanning (e.g. Skill-Spector) — this audit reasons about
  intent; a scanner catches known patterns at scale. Run both.
