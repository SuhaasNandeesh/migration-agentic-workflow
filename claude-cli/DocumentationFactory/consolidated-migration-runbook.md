# Consolidated DevOps Migration Summary Report

This report aggregates multi-repo status, FinOps cost targets, and security posture ratings.

## Repository Migration Pipelines

| Repository | Targets | Target Environments | Status |
| :--- | :--- | :--- | :--- |
| repo-01-infra | Azure | dev, test, prod | [Prepared & Verified] |
| repo-02-app-services | Azure | dev, prod | [Prepared & Verified] |

## Consolidated Security Guardrails
- Enforce OIDC Authentication: **Enforced** (OIDC default, secrets fallback compatible)
- Block Public Egress: **Enforced** (Private Endpoints + Private DNS mappings)
- AKS eBPF Dataplane: **Enforced** (Azure CNI Overlay powered by Cilium)

## Consolidated FinOps Right-Sizing Policies
- Dev/Test Compute sizes limited to: `Standard_B2s` / `Standard_D2s_v5` (Burstable)
- Dev/Test AKS autoscaling node boundaries: `1-2` nodes with template start/stop sleep scheduled
- Prod Node pools: `Standard_D4s_v5` with Spot VM scale-out pools enabled