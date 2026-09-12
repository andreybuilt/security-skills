# Kubernetes checklist

For manifests, Helm charts, kustomize, and admission policy. Map to the OWASP Kubernetes
Top 10 and CIS Kubernetes Benchmark.

## Pod / container security context
- `privileged: true` containers? (full host access — almost never justified)
- `allowPrivilegeEscalation` not set to `false`?
- Running as root (`runAsNonRoot` unset/false, `runAsUser: 0`)?
- Writable root filesystem (`readOnlyRootFilesystem` not true)?
- Dangerous Linux capabilities added (`SYS_ADMIN`, `NET_ADMIN`, `NET_RAW`); not dropping `ALL`?
- `hostNetwork`, `hostPID`, `hostIPC` true → breaks pod isolation?
- Host path mounts (`hostPath`), especially to `/`, `/var/run/docker.sock`, or node config?

## RBAC
- ClusterRole with `*` verbs/resources, or bound to `system:authenticated` / wide groups?
- ServiceAccount tokens auto-mounted into pods that do not call the API?
- Permissions to create pods / exec / impersonate / read secrets cluster-wide → escalation paths?
- `cluster-admin` bound to a workload ServiceAccount?

## Secrets & config
- Secrets in plain ConfigMaps or env vars instead of Secret objects / external secret stores?
- Secrets baked into images or Helm `values.yaml` checked into git?
- No encryption at rest for etcd secrets (cluster-level, note if unknowable from manifest)?

## Network & exposure
- No NetworkPolicy → default-allow east-west traffic?
- Services exposed via LoadBalancer/NodePort that should be ClusterIP/internal?
- Ingress without TLS, or with overly broad host/path rules?

## Images & supply chain
- Images by mutable tag (`:latest`) instead of digest?
- Images from untrusted registries; no image-pull policy / signature verification?
- No admission control (PSA/PSS, OPA/Kyverno) enforcing the above?

## Resource & availability
- No resource requests/limits → noisy-neighbor / DoS risk?
- No liveness/readiness probes on critical workloads?
