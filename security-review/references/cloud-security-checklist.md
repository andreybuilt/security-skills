# Cloud security checklist

For Terraform / CloudFormation / Pulumi / Bicep, IAM policies, and cloud console exports.
Map to CIS Foundations and the cloud provider's well-architected security pillar.

## Identity & access (the #1 cloud risk)
- IAM policy with `Action: "*"` or `Resource: "*"` where it is not strictly required? (least privilege)
- `iam:PassRole` scoped to `*` → privilege escalation via service role passing?
- Wildcard principals (`Principal: "*"`) on resource policies (S3, SQS, SNS, KMS, Lambda)?
- AssumeRole trust policies that trust an entire account or external account without a condition/ExternalId?
- Long-lived access keys where a role / OIDC would work? Keys not rotated?
- Admin (`AdministratorAccess`, `Owner`, `roles/owner`) granted to humans or CI?

## Data storage exposure
- S3 / GCS / Blob buckets public, or ACLs/policies allowing anonymous or all-AWS access?
- Block-public-access (or equivalent) disabled at account/bucket level?
- Storage, RDS/managed DB, EBS/disks unencrypted at rest? (CIS)
- Snapshots / AMIs shared publicly or with unknown accounts?
- Databases / caches (RDS, Redis, Elasticsearch, Mongo) reachable from `0.0.0.0/0`?

## Network
- Security groups / firewall rules opening 22, 3389, or DB ports to `0.0.0.0/0`?
- Overly broad egress where egress filtering matters?
- No VPC / private subnets for backend tiers; public IPs on internal resources?
- TLS not enforced (HTTP listeners, `aws_*` allowing non-SSL, weak TLS policy)?

## Secrets & config
- Secrets in Terraform variables, state, user-data, env, or plaintext in the template?
- Secrets manager / KMS not used where secrets are handled?
- KMS keys with overly permissive key policies or no rotation?

## Logging & detection
- CloudTrail / audit logging disabled, not multi-region, or not log-validated?
- Flow logs / access logs off for critical resources?
- No alerting on root usage, IAM changes, or policy changes?

## Serverless / compute
- Lambda/Function env vars holding secrets in plaintext?
- Functions with broad execution roles?
- Public function URLs / API Gateway routes without auth?
- Containers/instances running as root or with host networking?
