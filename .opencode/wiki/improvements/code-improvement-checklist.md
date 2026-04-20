---
id: code-improvement-checklist
last_updated: "2026-04-19"
used_by: [developer, code-reviewer]
---
# Code Improvement Checklist

This checklist is referenced by the developer and code-reviewer agents. During migration, the developer MUST apply these improvements. The code-reviewer MUST verify they were applied.

## Improvement Patterns

| # | Source Code Problem | Required Improvement | Severity if Missing |
|---|---------------------|---------------------|:-------------------:|
| 1 | Hardcoded values (IPs, CIDRs, sizes, regions) | Extract to `variable` blocks with descriptions, types, defaults, and validation | critical |
| 2 | Missing variable descriptions | Add clear `description` to every variable | major |
| 3 | Missing variable validation | Add `validation` blocks for constrained values (CIDRs, regions, SKUs) | major |
| 4 | Repeated values across files | Extract to `locals` block and reference | minor |
| 5 | No tags/labels | Add comprehensive tags (environment, project, managed-by, cost-center) | major |
| 6 | Monolithic resource files | Split into logical modules (network, compute, security, data) | minor |
| 7 | Missing outputs | Add outputs for resource IDs, endpoints, and connection strings | minor |
| 8 | Hardcoded secrets/passwords | Replace with Key Vault / secret manager references | critical |
| 9 | No resource naming convention | Apply consistent naming: `<type>-<project>-<env>-<region>` | minor |
| 10 | Missing security defaults | Add NSG rules, encryption at rest, TLS enforcement, disable public access | major |
| 11 | No lifecycle/prevent_destroy | Add lifecycle rules for stateful resources (databases, storage) | major |
| 12 | Missing health checks/probes | Add liveness/readiness probes for K8s, health endpoints for services | minor |
| 13 | Permissive IAM/RBAC | Apply least-privilege principle, use managed identities | major |
| 14 | Missing resource limits | Add CPU/memory limits for containers, SKU sizing for cloud resources | minor |
| 15 | No documentation comments | Add inline comments explaining non-obvious configuration choices | minor |

## Review Criteria

When reviewing migrated code, check:
- **No hardcoded values carried over** → if found → **FAIL (critical)**
- **All variables have descriptions** → if missing → **FAIL (major)**
- **All resources have tags** → if missing → **FAIL (major)**
- **Security hardened** → encryption, TLS, managed identity → if missing → **FAIL (major)**
- **Naming conventions applied** → `<type>-<project>-<env>-<region>` → if inconsistent → **FAIL (minor)**

## Scoring
- 0 critical issues + 0-2 major issues → **PASS**
- 0 critical + 3+ major → **FAIL**
- Any critical → **FAIL**
