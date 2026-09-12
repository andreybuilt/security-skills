# Review workflow (deep)

Read this when the input is large, spans multiple artifact types, or needs a real
threat-modeling pass rather than a quick lint.

## 1. Scope detection

Classify the input before reading it for bugs:

- **AppSec** — source files, a diff, a PR.
- **Cloud** — Terraform / CloudFormation / Pulumi / Bicep, IAM policies, console exports.
- **Kubernetes** — manifests, Helm charts, kustomize, admission policy.
- **CI/CD** — GitHub Actions, GitLab CI, Jenkinsfile, CircleCI, build/release scripts.
- **PR** — a diff plus a description; review the *change*, not the whole repo.

Most real reviews are mixed. Pick the primary scope, list the secondary ones, and load the
matching checklists.

## 2. Context extraction

Write this down before looking for issues. It is the difference between a threat model and
a lint pass.

- **Components** — what services / modules / resources are in play.
- **Trust boundaries** — where untrusted data crosses into trusted code; tenant edges;
  internal vs internet-facing.
- **Identities & roles** — who/what runs this, with what privileges.
- **Data flows** — where input comes from, where it goes, what is persisted.
- **External inputs** — request params, headers, files, queue messages, webhooks, env.
- **Secrets** — where they live, how they are injected, who can read them.
- **Deployment path** — how the artifact reaches production.

Anything not visible in the input is an **assumption**. Label it. Do not invent it.

## 3. Risk analysis

Walk the relevant checklist(s). For each item, ask the concrete question — "does this
artifact have this problem?" — and either point at evidence or move on. Do not list a
category you could not tie to the code.

Threat-model the data flows you wrote in step 2: for each boundary crossing, ask what an
attacker controlling the untrusted side could do. STRIDE is a fine prompt
(Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of
privilege) — use it to generate questions, not to pad the report.

## 4. Finding validation

Every candidate gets a status:

- **Confirmed** — evidence is in the artifact.
- **Suspected** — risky pattern, runtime context unclear.
- **Needs Validation** — depends on something you were not shown.

If you cannot decide, default to Suspected and write the one fact that would move it to
Confirmed.

## 5. Severity

Apply `severity-model.md` to each finding. Chain composable Mediums into a single
higher-severity finding when they combine into real impact.

## 6. Remediation

Write fixes an engineer can paste. Pull canonical patterns from
`remediation-patterns.md`. Show before/after. For Suspected findings, make the fix
conditional on the stated assumption.

## 7. Output

- 3+ findings or leadership audience → Executive summary + findings.
- 1-2 issues → Finding format.
- A diff / review request → PR comment format.

Always include an "Out of scope / not reviewed" line so the reader knows the boundary of
what you looked at.

## Multi-artifact tips

- Review shared infrastructure once and reference it, rather than repeating the same IAM
  finding per service.
- When a CI pipeline injects a secret that a Helm chart consumes that a container reads,
  that is one cross-cutting finding — describe the whole chain.
- If the artifacts contradict each other (a policy says one thing, the code does another),
  surface both. Do not silently pick one.
