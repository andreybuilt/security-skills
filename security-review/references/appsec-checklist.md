# AppSec checklist

For application code and PR diffs. Treat each item as a question against the artifact, not a
box to tick. Map to OWASP ASVS / Top 10 where it helps the reader.

## Input handling & injection
- User input concatenated into SQL, shell, LDAP, XPath, or NoSQL queries? (CWE-89, ASVS V5.3)
- Command execution with user-influenced arguments? (`os.system`, `exec`, `subprocess(shell=True)`)
- Output rendered into HTML/JS/attributes without context-aware encoding → XSS? (ASVS V5.3.3)
- Deserialization of untrusted data (pickle, native Java/PHP serialization, YAML load)? (CWE-502)
- Path built from user input → path traversal / arbitrary file read-write? (CWE-22)
- Server-side requests built from user input → SSRF, esp. to cloud metadata? (CWE-918)
- Template engine fed user input → SSTI?

## AuthN / AuthZ
- Object access checked against the *caller's* identity, or just by ID → IDOR / BOLA? (API Top 10 #1)
- Function/endpoint-level authorization present on every privileged action? (BFLA)
- Authentication on all non-public routes; no "security by obscurity" endpoints?
- Session tokens: secure flags, rotation on login, sane expiry; JWT `alg` not `none`, signature verified?
- Password storage with a slow salted hash (bcrypt/scrypt/argon2), never MD5/SHA-1/plaintext?
- Multi-step flows (password reset, email change) that can be skipped or replayed?

## Secrets & crypto
- Hardcoded credentials, API keys, tokens, private keys in source or config?
- Secrets logged, returned in errors, or sent to analytics?
- Weak crypto (ECB, static IV, MD5/SHA-1 for integrity, homemade crypto)? (ASVS V6)
- Randomness from a non-CSPRNG for tokens/secrets? (`random` vs `secrets`/`crypto`)

## Data exposure & errors
- Verbose errors / stack traces returned to clients? (CWE-209)
- Sensitive fields over-returned by an API (mass assignment, serializer leaks)?
- PII/secrets written to logs?
- Debug mode, admin endpoints, or test backdoors reachable in prod?

## Business logic & state
- Race conditions on balance/inventory/quota (TOCTOU)?
- Missing rate limiting on auth, OTP, or expensive endpoints?
- Trusting client-supplied price/role/quantity/flags?
- File upload: type/size validation, stored outside web root, no execution?

## Dependencies
- Known-vulnerable libraries actually reachable by the code path?
- Unpinned or floating dependency versions in the manifest?
