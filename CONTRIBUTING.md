# Contributing

New detections, fixtures and checklist corrections are welcome.

## Before you open a pull request

```bash
./tests/run-all.sh
```

It must end in `ALL CHECKS PASSED`, and CI runs the same command on every pull request.

## Rules for a change

1. **Fixtures come in pairs.** Every new file in `tests/fixtures/malicious/` needs a same-named file in
   `tests/fixtures/benign/`: the same content with only the defect removed. Two files that differ for
   other reasons prove nothing about the defect.
2. **Decide the tier on purpose.** HIGH is for content with no ordinary reason to exist (hidden
   characters, undecodable files) and fails the default run. WARN is for signals a human should weigh
   and fails only under `--strict`. Do not promote a phrase match to HIGH.
3. **The scanner stays standard library only**, and runs outside any agent session.
4. **The published skills must self-scan clean.** The suite scans `security-review/` and `skill-audit/`
   and fails on any HIGH finding, so an example payload belongs in a fixture, never in a skill file.
5. **No identifiers.** The leak sweep fails the build on your own username and home directory, so run
   the suite on your machine before pushing.
6. **Update "What this does not catch"** when a change opens or closes an evasion.
