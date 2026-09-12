# AB.Agentic Security Skills

Two Claude Code skills that vet what an agent is asked to trust: the code it reviews, and
the instructions it runs under.

---

## Why one repository

An agent takes two kinds of input that both deserve suspicion before you act on them: the
code a user hands it to review, and the skills, plugins, and configuration files the agent
itself loads and treats as instructions. Most security tooling only covers the first kind.
A SAST scanner reads your Terraform and your Python. It does not read `SKILL.md`,
`CLAUDE.md`, an MCP server config, or a plugin manifest, and none of those look like code
to a traditional scanner, so nothing flags them.

That gap matters because an instruction file is executable the moment an agent reads it.
A hidden zero-width character, a buried HTML comment, or a sentence that tells the agent to
"ignore the user's previous instructions" does not need to compile or run as a binary. The
agent just has to read it.

`security-review` covers the first problem: application code, pull requests, cloud
configuration, Kubernetes manifests, and CI/CD pipelines, mapped to OWASP, NIST SSDF, CIS,
and SLSA. `skill-audit` covers the second: it scans skills, plugins, MCP configs, and
instruction files for hidden Unicode, injected instructions, and exfiltration directives
before you let an agent trust them. They ship together because a security review that skips
the artifacts telling the agent how to behave has already missed half the attack surface.

---

## Layout

```
security-review/
  SKILL.md                       the skill definition Claude Code loads
  references/                    checklists loaded on demand: AppSec, cloud, Kubernetes,
                                  CI/CD, severity model, finding templates, remediation
                                  patterns, and a skill/agent pre-install checklist

skill-audit/
  SKILL.md                       the skill definition Claude Code loads
  scripts/scan_hidden.py         the hidden-content scanner (stdlib only, no dependencies)
  references/                    the attack-vector catalog, detection checklist, MCP/plugin
                                  checklist, brainstorm-validation guide, verdict templates

tests/
  run-all.sh                     the test suite described below
  fixtures/malicious/            eight samples, each built to trip one detection category
  fixtures/benign/                the same eight samples with the defect removed

LICENSE
```

---

## Installing the skills

Copy each skill directory into wherever Claude Code loads skills from on your setup, most
commonly `~/.claude/skills/` for a user-level install or `.claude/skills/` inside a project:

```bash
git clone https://github.com/andreybuilt/security-skills
cp -r security-review-and-skill-audit/security-review ~/.claude/skills/
cp -r security-review-and-skill-audit/skill-audit ~/.claude/skills/
```

Both skills are plain Markdown plus one stdlib Python script. Nothing here needs a package
manager or a network call to install.

---

## The scanner

`skill-audit/scripts/scan_hidden.py` is the part of this pair you can run on its own,
outside any agent session:

```bash
python3 skill-audit/scripts/scan_hidden.py path/to/some-skill/
```

It reads the raw bytes of every text file under a path and flags eight things: zero-width
and bidirectional-override characters, Unicode tag smuggling, HTML comments that can carry
a hidden instruction, and three phrase groups covering goal-override language, data
exfiltration, and config or command-execution tampering. Findings split into two tiers.
HIGH covers hidden or invisible characters and files the script cannot even decode as
UTF-8; the exit code turns non-zero on any HIGH finding, which is what makes the script
usable as a CI gate. WARN covers HTML comments, standalone emoji variation selectors, and
the phrase groups; these print for a human to weigh and do not fail the run unless you pass
`--strict`. An emoji written correctly, like a warning sign followed by its variation
selector, never trips this scanner. The same variation-selector character with no emoji in
front of it does, because that shape has no ordinary reason to appear and matches a known
smuggling channel.

---

## Tests

```bash
./tests/run-all.sh
```

The suite runs four kinds of check, and the second one is the point of this section: a
static fixture corpus only tells you the scanner treats a malicious file differently from a
benign one, and two files can differ for reasons that have nothing to do with the defect
you meant to test. So beyond the eight malicious/benign pairs, the suite also takes a
single clean file, plants one defect into it, runs the scanner and confirms it now fails
and names that exact file, then strips the same defect back out of the same file and
confirms the scanner passes it again. Two categories get this live treatment: a hidden
zero-width character (HIGH) and a goal-override phrase (WARN, checked under `--strict`).
A suite that only proves the violating direction would have let last year's HTML-comment
false-positive regression ship again; this one has to clear both directions before it
counts as passing.

The suite closes with a self-scan: it runs the scanner over `security-review/` and
`skill-audit/` themselves and requires zero HIGH findings, since a tool that fails its own
audit has no business auditing anyone else's skill. It also runs a leak sweep whose pattern
is assembled at run time from `$(id -un)` and `$HOME` rather than written as a literal
string, so the check file that enforces "no identifiers in this repository" does not
itself become the one place an identifier survives.

Real output from a clean run:

```
== syntax ==
  ok    skill-audit/scripts/scan_hidden.py

== fixture corpus: malicious samples must fire ==
  ok    01_zero_width_smuggle.md (exit 1, named in output)
  ok    02_bidi_override.md (exit 1, named in output)
  ok    08_unreadable_binary.md (exit 1, named in output)
  ok    03_hidden_html_comment.md (--strict exit 1, named in output)
  ok    04_injection_phrase.md (--strict exit 1, named in output)
  ok    05_exfil_directive.md (--strict exit 1, named in output)
  ok    06_config_rce.md (--strict exit 1, named in output)
  ok    07_standalone_variation_selector.md (--strict exit 1, named in output)

== fixture corpus: benign counterparts must pass ==
  ok    01_zero_width_smuggle.md (--strict exit 0)
  ok    02_bidi_override.md (--strict exit 0)
  ok    08_unreadable_binary.md (--strict exit 0)
  ok    03_hidden_html_comment.md (--strict exit 0)
  ok    04_injection_phrase.md (--strict exit 0)
  ok    05_exfil_directive.md (--strict exit 0)
  ok    06_config_rce.md (--strict exit 0)
  ok    07_standalone_variation_selector.md (--strict exit 0)

== plant-then-remove: hidden zero-width character ==
  ok    before planting: clean file passes (exit 0)
  ok    after planting: scanner fires (exit 1, names the file, names ZERO WIDTH SPACE)
  ok    after removing: same file passes again (exit 0)

== plant-then-remove: goal-override phrase (WARN, needs --strict) ==
  ok    before planting: clean file passes --strict (exit 0)
  ok    after planting: --strict fires (exit 1, names the file, names INJECTION)
  ok    after removing: same file passes --strict again (exit 0)

== self-scan: published skill content carries no HIGH finding ==
  ok    security-review/ and skill-audit/ scan clean of HIGH findings

== no leaked identifiers ==
  ok    none found

ALL CHECKS PASSED
```

---

## What this does not catch

The phrase groups (goal-override, exfiltration, config/RCE) match literal substrings,
case-insensitively. An attacker who rewrites "ignore previous instructions" as "disregard
what you were told earlier" or splits `curl` and its argument across two lines defeats the
match without changing what the instruction does. The same is true of homoglyph attacks:
swapping a Latin `a` for a visually identical Cyrillic а defeats every phrase check built on
literal ASCII text, and this scanner has no homoglyph normalization pass. None of this makes
the phrase groups useless. It marks them as WARN rather than HIGH for exactly this reason:
they are signals for a human to weigh, not proof of anything, and the tool says so in its
own output. The HIGH tier (hidden Unicode, unreadable files) is a harder guarantee, because
those code points have no ordinary reason to appear in instruction text regardless of how
the surrounding sentence is worded.

This project carries no production numbers. Two skills, one scanner script, and a test
suite built for this release are what is here; nothing below claims a deployment history it
does not have.

---

## License

MIT. See [LICENSE](LICENSE).
