#!/usr/bin/env python3
"""
scan_hidden.py — surface hidden/invisible content and instruction-injection signals in
AI instruction files (skills, .md/.mdc/.cursorrules, AGENTS.md/CLAUDE.md, prompts, MCP/plugin
configs) BEFORE an AI agent processes them.

Part of the `skill-audit` skill. Defensive use only: it reveals deliberately hidden content
so a human can reject a poisoned file. It does not modify anything.

Detects:
  - Invisible / non-printing Unicode: zero-width chars, bidi controls, Unicode Tags,
    word joiners, variation selectors (Rules File Backdoor / CamoLeak class).
  - HTML comments and hidden-Markdown comment tricks.
  - High-signal instruction-injection and exfiltration / config-rewrite phrases.

Usage:
  python3 scan_hidden.py <file_or_dir> [<file_or_dir> ...]
  python3 scan_hidden.py .            # scan a whole skill/plugin bundle
Exit code: 0 = clean, 1 = findings, 2 = usage error.

Pure stdlib; runs on stock macOS python3.
"""

import os
import sys
import unicodedata

# Two tiers. HIGH = invisible/control code points with no business in instruction text
# (real injection-smuggling vectors); these fail the scan. LOW = code points that are
# usually benign in practice (emoji variation selectors) but worth noting; these warn only.
# Severity assigned per code point so emoji (⚠️ = base + U+FE0F) does not read as an attack.
SUSPECT_SINGLE = {
    0x200B: ("ZERO WIDTH SPACE", "HIGH"),
    0x200C: ("ZERO WIDTH NON-JOINER", "HIGH"),
    0x200D: ("ZERO WIDTH JOINER", "HIGH"),
    0x2060: ("WORD JOINER", "HIGH"),
    0x180E: ("MONGOLIAN VOWEL SEPARATOR", "HIGH"),
    0xFEFF: ("ZERO WIDTH NO-BREAK SPACE / BOM", "HIGH"),
}
SUSPECT_RANGES = [
    (0x200E, 0x200F, "LEFT/RIGHT-TO-LEFT MARK", "HIGH"),
    (0x202A, 0x202E, "BIDIRECTIONAL EMBEDDING/OVERRIDE", "HIGH"),
    (0x2066, 0x2069, "BIDIRECTIONAL ISOLATE", "HIGH"),
    (0x2061, 0x2064, "INVISIBLE MATH OPERATOR", "HIGH"),
    (0xE0000, 0xE007F, "UNICODE TAG (invisible ASCII smuggling)", "HIGH"),
    (0xE0100, 0xE01EF, "VARIATION SELECTOR SUPPLEMENT", "HIGH"),
    # NOTE: emoji/text variation selectors (U+FE00-FE0F) are handled separately in scan_file:
    # benign when attached to an emoji base (⚠️, ✅), WARN when standalone (possible smuggling).
]


def is_emoji_base(ch):
    """True if ch is an emoji/symbol that legitimately takes a variation selector."""
    if not ch:
        return False
    cp = ord(ch)
    return (0x2190 <= cp <= 0x2BFF or      # arrows, symbols, dingbats, misc pictographs (⚠ ✅ ❤ ☎ …)
            0x2600 <= cp <= 0x27BF or
            0x1F000 <= cp <= 0x1FAFF or     # emoji supplementary planes
            cp in (0x203C, 0x2049, 0x3030, 0x303D))

# High-signal phrases. Case-insensitive substring match. Tuned for precision, not recall —
# the model still reads the file; this just flags the obvious ones for a human.
INJECTION_PHRASES = [
    "ignore previous", "ignore all previous", "disregard the above", "disregard previous",
    "you are now", "new instructions", "new system prompt", "system prompt:",
    "do not tell the user", "do not mention", "without telling", "keep this secret",
    "regardless of", "override", "always run", "before anything else", "first, run",
]
EXFIL_PHRASES = [
    "send to", "post to", "exfiltrate", "email the", "upload the", "curl ", "wget ",
    "http://", "https://hooks.", "webhook", ".env", "github_token", "aws_secret",
    "api key", "api_key", "private key", "id_rsa", "~/.ssh", "~/.aws", "keychain",
]
CONFIG_RCE_PHRASES = [
    "settings.json", "mcp.json", ".cursor/mcp", "allowed-tools", "allowedtools",
    "auto-approve", "autoapprove", "whitelist", "| bash", "| sh", "eval(", "exec(",
    "rm -rf", "git push", "chmod +x", "base64 -d", "base64 --decode",
]

TEXT_EXTS = {".md", ".mdc", ".cursorrules", ".txt", ".json", ".yaml", ".yml", ".toml",
             ".py", ".sh", ".js", ".ts", ".rules", ""}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def classify(cp):
    """Return (name, severity) for a suspect code point, or None."""
    if cp in SUSPECT_SINGLE:
        return SUSPECT_SINGLE[cp]
    for lo, hi, name, sev in SUSPECT_RANGES:
        if lo <= cp <= hi:
            return (name, sev)
    # Catch other format/control chars (category Cf/Cc) beyond ASCII, excl. common ones.
    if cp > 0x7F:
        cat = unicodedata.category(chr(cp))
        if cat in ("Cf", "Cc", "Co"):
            return ("FORMAT/CONTROL CHAR (%s)" % cat, "HIGH")
    return None


def safe(s):
    """Render a snippet with invisible chars made visible as <U+XXXX>."""
    out = []
    for ch in s:
        cp = ord(ch)
        if classify(cp) or cp in (0x09,) or (cp < 0x20 and cp not in (0x0A, 0x0D)):
            out.append("<U+%04X>" % cp)
        else:
            out.append(ch)
    return "".join(out)


def scan_file(path):
    """Return a list of (severity, category, line_no, detail). severity in {HIGH, WARN}."""
    hits = []
    try:
        with open(path, "r", encoding="utf-8", errors="surrogatepass") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, OSError) as e:
        return [("HIGH", "UNREADABLE", 0,
                 "cannot decode as UTF-8 text: %s - CANNOT CLEAR, inspect manually" % e)]

    for ln, line in enumerate(lines, 1):
        # 1. invisible / non-printing unicode (severity per code point)
        prev = ""
        for ch in line:
            cp = ord(ch)
            if 0xFE00 <= cp <= 0xFE0F:  # variation selector: benign on emoji, suspect alone
                if not is_emoji_base(prev):
                    hits.append(("WARN", "VARIATION_SELECTOR", ln,
                                 "standalone VS U+%04X (no emoji base): %s" % (cp, safe(line.strip())[:160])))
                prev = ch
                continue
            res = classify(cp)
            if res:
                name, sev = res
                hits.append((sev, "HIDDEN_UNICODE", ln,
                             "%s (U+%04X)  context: %s" % (name, cp, safe(line.strip())[:160])))
                break  # one report per line is enough
            prev = ch
        low = line.lower()
        # 2. HTML / markdown hidden comments (warn: can carry payloads, but mostly benign docs)
        if "<!--" in line or "[//]: #" in low or "display:none" in low.replace(" ", ""):
            hits.append(("WARN", "HIDDEN_MARKUP", ln, safe(line.strip())[:160]))
        # 3. phrase signals (warn: heuristic, human/LLM weighs intent)
        for grp, phrases in (("INJECTION", INJECTION_PHRASES),
                             ("EXFIL", EXFIL_PHRASES),
                             ("CONFIG/RCE", CONFIG_RCE_PHRASES)):
            for p in phrases:
                if p in low:
                    hits.append(("WARN", grp, ln, "matched %r: %s" % (p, line.strip()[:160])))
                    break
    return hits


def iter_targets(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for fn in files:
                    ext = os.path.splitext(fn)[1].lower()
                    if ext in TEXT_EXTS:
                        yield os.path.join(root, fn)
        elif os.path.isfile(p):
            yield p
        else:
            print("  ! not found: %s" % p, file=sys.stderr)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    strict = "--strict" in argv[1:]
    if not args:
        print(__doc__)
        return 2
    high_total = warn_total = scanned = 0
    for path in iter_targets(args):
        scanned += 1
        hits = scan_file(path)
        highs = [h for h in hits if h[0] == "HIGH"]
        warns = [h for h in hits if h[0] == "WARN"]
        if hits:
            print("\n=== %s ===" % path)
            for sev, cat, ln, detail in highs + warns:
                loc = ("L%d" % ln) if ln else "-"
                print("  [%-4s %-13s] %-5s %s" % (sev, cat, loc, detail))
        high_total += len(highs)
        warn_total += len(warns)
    verdict = ("HIGH-RISK - do not deploy until inspected" if high_total
               else ("WARNINGS ONLY - review, likely benign" if warn_total else "CLEAN"))
    print("\n%s - %d file(s) scanned, %d high-risk, %d warning(s)." %
          (verdict, scanned, high_total, warn_total))
    print("HIGH = hidden/invisible Unicode or unreadable files (real smuggling vectors). "
          "WARN = HTML comments, emoji variation selectors, and heuristic phrase matches "
          "(signals for a human, not proof). Exit 1 on HIGH; use --strict to also fail on warnings. "
          "Complements, does not replace, manual audit.")
    return 1 if (high_total or (strict and warn_total)) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
