# Hidden-content scan (manual equivalent)

`scripts/scan_hidden.py` automates this. Use this page when you cannot run the script, or to
understand what it flags and verify a hit by hand.

## Why this comes first
Humans read rendered Markdown; AI reads the raw bytes. The Rules File Backdoor and CamoLeak
classes hide the payload in characters the human never sees. If you skip the raw pass, you
review a different document than the AI will.

## What to surface

### Invisible / non-printing Unicode
Flag any of these outside of legitimately non-Latin text:

| Range / char | Name | Why suspicious |
|---|---|---|
| U+200B | Zero-width space | Splits/hides tokens |
| U+200C / U+200D | ZWNJ / ZWJ | Hidden instruction encoding |
| U+FEFF | BOM / zero-width no-break | Hidden in body text |
| U+202A-202E, U+2066-2069 | Bidi controls | Text reads differently than it runs |
| U+E0000-E007F | Unicode Tags | Can encode hidden ASCII invisibly |
| U+2060, U+180E | Word joiner / MVS | Non-printing filler |
| Variation selectors (U+FE00-FE0F, U+E0100+) | — | Used to smuggle data |

### Hidden Markdown / HTML
- `<!-- ... -->` HTML comments (auto-injected context often still reads these).
- Markdown link-label comments: `[//]: # (instruction here)`.
- `<details>`-collapsed blocks, `display:none`, white or 1px text in embedded HTML.
- Lines padded with whitespace so text sits past the visible right margin.

## Manual commands (macOS)

```bash
# Reveal non-ASCII / non-printing bytes with their positions
grep -nP '[^\x00-\x7F]' file.md          # any non-ASCII line
perl -ne 'print "$.: $_" if /[\x{200B}-\x{200F}\x{202A}-\x{202E}\x{2060}-\x{206F}\x{FEFF}\x{E0000}-\x{E007F}]/' file.md

# Dump suspicious code points by line
python3 - <<'PY'
import sys,unicodedata
for i,l in enumerate(open("file.md",encoding="utf-8"),1):
    for ch in l:
        if ord(ch)>127 and (unicodedata.category(ch) in ("Cf","Cc","Co") or 0x200B<=ord(ch)<=0x206F):
            print(i, hex(ord(ch)), unicodedata.name(ch,"?"))
PY

# Find HTML comments and hidden-link Markdown comments
grep -nE '<!--|\[//\]: #' file.md
```

## Output tiers (v1.1+)
The scanner separates severity so it is usable as a CI gate without drowning in noise:
- **HIGH** — real hidden/invisible Unicode (zero-width, bidi, Unicode tags, VS supplement,
  control chars) and unreadable/obfuscated files. These fail the scan (exit 1).
- **WARN** — HTML comments, standalone variation selectors, and heuristic phrase matches.
  Reported for a human to weigh; they do not fail the scan by default.
- Emoji variation selectors (⚠️, ✅, ❤️) are treated as benign and not reported, because the
  selector is attached to an emoji base. A variation selector with no emoji base is WARNed
  (possible steganographic smuggling).
- `--strict` makes warnings fail too. Exit 0 = no HIGH (clean enough to deploy/commit).

## Verifying a hit
When the scanner flags something, render it visible — show the code point and surrounding
text so a human can confirm it is hostile, e.g. `"deploy<U+200B>the<U+200B>backdoor"`. Never
silently strip it and move on; the presence of deliberate invisible content is itself a
finding.
