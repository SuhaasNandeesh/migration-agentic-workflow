---
name: testing
description: "Provides test execution patterns, tool commands, and validation scripts for testing migrated artifacts across any platform."
metadata:
  version: "1.0"
---
# Testing

Test execution patterns for validating migrated artifacts.

## Test Tools by File Type

| File Type | Tools | Install Command |
|-----------|-------|----------------|
| Terraform | `terraform validate`, `terraform plan`, `tfsec`, `checkov` | `brew install terraform tfsec checkov` |
| Kubernetes YAML | `kubeconform`, `kubectl --dry-run`, `yamllint` | `brew install kubeconform yamllint` |
| Helm Charts | `helm lint`, `helm template` | `brew install helm` |
| GitHub Actions | `actionlint`, `yamllint` | `brew install actionlint yamllint` |
| Dockerfiles | `hadolint` | `brew install hadolint` |
| Shell scripts | `shellcheck` | `brew install shellcheck` |
| JSON files | `python3 -m json.tool` | built-in |
| YAML files | `yamllint` | `brew install yamllint` |
| Prometheus rules | `promtool check rules` | `brew install prometheus` |

## Test Priority
1. **P0 — Syntax:** Does the file parse? (blocks everything)
2. **P1 — Schema:** Does it match the expected format? (blocks deployment)
3. **P2 — Execution:** Does it plan/template/dry-run? (blocks deployment)
4. **P3 — Security:** Does it pass security linting? (blocks production)
5. **P4 — Best practices:** Any linter warnings? (advisory)

## Fallback Strategy
If a specialized tool is not installed:
1. Try YAML/JSON syntax validation as minimum
2. Log the missing tool in `tools_not_found`
3. DO NOT skip the file — validate what you can
