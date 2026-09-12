# CI/CD & supply-chain checklist

For GitHub Actions, GitLab CI, Jenkinsfiles, CircleCI, and build/release scripts. Map to
OWASP Top 10 CI/CD Risks and SLSA.

## Workflow triggers & untrusted input
- `pull_request_target` (or equivalent) running with secrets while checking out untrusted PR code? (CICD-SEC-4)
- Untrusted input (`github.event.*`, PR title/branch/body) interpolated into a `run:` shell step → script injection? (CWE-94)
- Workflows that build/deploy on fork PRs with access to secrets?

## Dependency & action pinning (supply chain)
- Third-party actions pinned to a full commit SHA, not a mutable tag (`@v3`, `@main`)? (SLSA, CICD-SEC-3)
- Build dependencies / base images pinned and integrity-checked (lockfiles, digests)?
- `curl | bash` or fetching install scripts from the internet at build time?
- Internal package names that could be claimed publicly → dependency confusion?

## Secrets in pipelines
- Secrets echoed, printed, or written to logs/artifacts?
- Secrets available to steps that do not need them (no scoping / no environments)?
- Long-lived cloud credentials stored as CI secrets instead of OIDC federation? (prefer OIDC)
- Secrets passed via command-line args (visible in process list / logs)?

## Permissions & isolation
- Default `GITHUB_TOKEN` / job token at write/admin when read is enough? (`permissions:` least privilege)
- Self-hosted runners on public repos (reusable across untrusted jobs)?
- Build steps with network access they do not need (no egress control on builds)?

## Artifact integrity & release
- Artifacts signed / provenance attested (SLSA provenance, cosign)?
- Release/deploy steps gated by review/approval, or can one person push to prod?
- Deploy credentials scoped to the target environment only?

## Repo hygiene
- Branch protection / required reviews on the default and release branches?
- Secrets committed in history (scan with gitleaks/trufflehog)?
- Auto-merge or auto-approve bots that bypass review?
