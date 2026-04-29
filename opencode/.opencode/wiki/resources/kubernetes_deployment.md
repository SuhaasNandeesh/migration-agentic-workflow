---
resource: kubernetes_deployment
kind: Deployment
api_version: apps/v1
last_updated: "2026-04-22"
source_runs: 0
---
# Kubernetes Deployment

## Overview
Standard Kubernetes Deployment resource for managing stateless application pods.

## Key Migration Points (EKS → AKS)
- **Image registry:** Change ECR refs to ACR (`<account>.dkr.ecr.<region>.amazonaws.com` → `<registry>.azurecr.io`)
- **Service account:** Replace IRSA annotation with Azure Workload Identity annotation
- **Node selector:** Replace EKS-specific labels with AKS labels
- **Resource limits:** Verify CPU/memory fit AKS node pool VM SKUs
- **Tolerations:** Update any EKS-specific taints/tolerations

## Required Fields
- `metadata.name`
- `metadata.namespace` (never use `default`)
- `spec.replicas`
- `spec.selector.matchLabels`
- `spec.template.spec.containers[].resources.limits`
- `spec.template.spec.containers[].resources.requests`
- `spec.template.spec.containers[].livenessProbe`
- `spec.template.spec.containers[].readinessProbe`

## Best Practices
- Always set resource requests AND limits
- Always set liveness and readiness probes
- Use `RollingUpdate` strategy with `maxSurge: 1` and `maxUnavailable: 0` for zero-downtime
- Use `podDisruptionBudget` for critical workloads
- Set `securityContext.runAsNonRoot: true`
- Never use `latest` tag — always pin image versions

## Gotchas
- AKS virtual nodes (ACI) don't support all Deployment features (hostPath, daemonsets)
- AKS node auto-scaling may take 2-5 minutes to add nodes — set appropriate resource requests
- ACR pull requires `imagePullSecrets` or managed identity ACR integration

## Related
- [[kubernetes_service]]
- [[eks-to-aks-manifests]]
