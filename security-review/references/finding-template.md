# Finding template

Use this exact structure for each issue. A filled example follows.

```
Finding: <concrete title — name the actual issue, not the category>
Severity: Critical / High / Medium / Low / Informational
Status: Confirmed / Suspected / Needs Validation
Affected component: <file:line, resource ARN, workflow name, …>
Evidence:
  <the specific code / config / behavior, quoted exactly and minimally>
Impact:
  <what an attacker or operator could cause>
Exploitability:
  <preconditions: auth, network position, user interaction, exposure, known chain>
Recommended fix:
  <specific change, with a code/config snippet>
Validation:
  <how to confirm the fix worked>
Business risk (High+):
  <data class, regulatory exposure, blast radius>
References:
  <CWE-XXX, OWASP ASVS V-X, CIS X.Y>
```

## Worked example

```
Finding: SQL injection in user lookup endpoint
Severity: High
Status: Confirmed
Affected component: app/api/users.py:47

Evidence:
  cursor.execute(f"SELECT * FROM users WHERE id = {request.args['id']}")

Impact:
  An authenticated user can read or modify arbitrary rows by injecting SQL through the
  `id` parameter — full read of the users table, including password hashes.

Exploitability:
  Requires a valid session (any authenticated user). No special tooling; a single crafted
  query string. Endpoint is internal-API but reachable by every logged-in account.

Recommended fix:
  Use a parameterized query — never format user input into SQL.
    cursor.execute("SELECT * FROM users WHERE id = %s", (request.args['id'],))
  Also validate that `id` is an integer before the call.

Validation:
  Send `id=1 OR 1=1` and confirm it returns no rows / a 400, not the full table. Add a
  regression test for the injection payload.

Business risk:
  Exposes PII and credential hashes for all users. Likely in scope for GDPR/CCPA breach
  notification if exploited.

References:
  CWE-89, OWASP ASVS V5.3.4, OWASP Top 10 A03:2021 (Injection)
```

## Notes

- Quote evidence; do not paraphrase it. The reader should be able to grep for it.
- One finding per issue. If the same root cause appears in five places, list it once with
  all five locations under Affected component.
- If Status is Suspected or Needs Validation, the Recommended fix can be conditional —
  state the assumption.
