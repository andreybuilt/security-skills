# Remediation patterns

Canonical fixes to paste into the "Recommended fix" section. Adapt to the artifact's
language/stack; keep the principle.

## SQL injection → parameterized queries
```python
# Bad
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
# Good
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```
Use the ORM/query builder's binding; never string-format user input into SQL.

## XSS → context-aware output encoding
- Render through a template engine with auto-escaping on (Jinja2, React JSX, etc.).
- For HTML attributes, JS contexts, and URLs use the matching encoder — HTML-escaping is
  not enough inside a `<script>` or `href`.
- Set a Content-Security-Policy as defense in depth.

## Command injection → no shell, pass args as a list
```python
# Bad
os.system(f"convert {filename} out.png")
# Good
subprocess.run(["convert", filename, "out.png"], shell=False, check=True)
```
Validate/allowlist `filename` first.

## Secrets → out of code, into a manager
- Remove the secret, rotate it (assume it is burned once committed), then load from a
  secret manager (AWS Secrets Manager, Vault, GCP Secret Manager, K8s Secret + external store).
- Add the path to `.gitignore`; scan history with gitleaks/trufflehog and purge if found.

## IAM → least privilege
```hcl
# Bad
Action = "*"  Resource = "*"
# Good — scope action and resource
Action   = ["s3:GetObject"]
Resource = ["arn:aws:s3:::my-bucket/uploads/*"]
```
Replace `iam:PassRole "*"` with the specific role ARN(s). Add conditions (source IP,
`aws:SourceArn`, ExternalId) on trust policies.

## CI cloud creds → OIDC federation
Replace long-lived `AWS_ACCESS_KEY_ID` CI secrets with the provider's OIDC trust:
`role-to-assume` + `id-token: write` permission, role trust scoped to the specific repo and
branch. No standing keys to leak.

## CI action pinning → commit SHA
```yaml
# Bad
uses: some/action@v3
# Good
uses: some/action@<full-40-char-sha>  # v3.1.2
```

## CI script injection → env indirection
```yaml
# Bad
run: echo "Title: ${{ github.event.pull_request.title }}"
# Good
env:
  TITLE: ${{ github.event.pull_request.title }}
run: echo "Title: $TITLE"
```

## Auth tokens → safe defaults
- Cookies: `Secure`, `HttpOnly`, `SameSite=Lax/Strict`; rotate session on login.
- JWT: verify signature, reject `alg: none`, pin expected `alg`, check `exp`/`aud`/`iss`.

## Passwords → slow salted hash
Use argon2id (or bcrypt/scrypt) with sane parameters. Never MD5/SHA-1/SHA-256-plain.

## Kubernetes → hardened securityContext
```yaml
securityContext:
  runAsNonRoot: true
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
```
Add a default-deny NetworkPolicy and resource requests/limits per workload.

## Path traversal → resolve and confine
Canonicalize the path and verify it stays within the intended base directory before use;
reject `..` and absolute paths.

## SSRF → allowlist + block metadata
Allowlist destination hosts/schemes; block link-local/metadata ranges (169.254.169.254,
fd00:ec2::254); disable redirects to internal ranges.
