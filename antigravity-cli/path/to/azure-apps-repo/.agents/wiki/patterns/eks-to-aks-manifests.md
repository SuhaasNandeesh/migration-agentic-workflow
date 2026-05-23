---
pattern: eks-to-aks-manifests
complexity: functional
last_updated: "2026-04-22"
source_runs: 0
---
# EKS to AKS Kubernetes Manifest Migration

## Migration Steps

1. **Annotations:** Remove `eks.amazonaws.com/*` annotations → add `azure.workload.identity/*` if needed
2. **Service accounts:** Remove `eks.amazonaws.com/role-arn` annotation → add `azure.workload.identity/client-id`
3. **Storage classes:** `gp2`/`gp3` → `managed-premium` or `managed-csi`
4. **Ingress class:** `alb` → `azure/application-gateway` or `nginx`
5. **Load balancer annotations:** `service.beta.kubernetes.io/aws-*` → `service.beta.kubernetes.io/azure-*`
6. **Node selectors:** `eks.amazonaws.com/nodegroup` → `agentpool` or custom labels
7. **ECR references:** `<account>.dkr.ecr.<region>.amazonaws.com` → `<registry>.azurecr.io`
8. **IAM/IRSA:** `serviceAccountAnnotations` with ARN → Azure Workload Identity federation
9. **Resource limits:** Verify sizes map to AKS node pool SKUs
10. **Persistent volumes:** EBS CSI → Azure Disk CSI, EFS CSI → Azure Files CSI

## Common Annotation Mapping

| EKS Annotation | AKS Equivalent |
|---------------|----------------|
| `eks.amazonaws.com/role-arn` | `azure.workload.identity/client-id` |
| `service.beta.kubernetes.io/aws-load-balancer-type: nlb` | `service.beta.kubernetes.io/azure-load-balancer-internal: "true"` |
| `service.beta.kubernetes.io/aws-load-balancer-internal: "true"` | `service.beta.kubernetes.io/azure-load-balancer-internal: "true"` |
| `service.beta.kubernetes.io/aws-load-balancer-ssl-cert` | Use AGIC or ingress-nginx with cert-manager |

## Storage Class Mapping

| EKS | AKS | Notes |
|-----|-----|-------|
| `gp2` | `managed` | Standard HDD |
| `gp3` | `managed-csi-premium` | Premium SSD |
| `io1` / `io2` | `managed-csi-premium` | Ultra available for extreme IOPS |
| `efs` (EFS CSI) | `azurefile-csi-premium` | Shared file storage |

## Gotchas
- EKS uses IRSA (IAM Roles for Service Accounts) → AKS uses Workload Identity (federated OIDC)
- EKS ALB Ingress Controller → AKS uses AGIC (Application Gateway Ingress Controller) or nginx
- ECR image references must be updated to ACR
- EKS node groups → AKS node pools (different scaling config)
- EKS Fargate profiles have no direct AKS equivalent → use virtual nodes or regular node pools
- Cluster Autoscaler config differs between EKS and AKS

## Validation Criteria
- No AWS-specific annotations remain
- No ECR image references remain
- All storage classes reference Azure CSI drivers
- Service accounts have correct Workload Identity annotations
- Ingress resources use AKS-compatible ingress class

## Related
- [[aks-workload-identity]]
- [[ecr-to-acr]]
