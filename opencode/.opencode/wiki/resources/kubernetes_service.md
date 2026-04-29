---
resource: kubernetes_service
kind: Service
api_version: v1
last_updated: "2026-04-22"
source_runs: 0
---
# Kubernetes Service

## Overview
Exposes Deployment pods as a network service. Key resource for routing traffic.

## Key Migration Points (EKS → AKS)
- **LoadBalancer annotations:** Replace AWS-specific annotations with Azure equivalents
- **Internal LB:** `service.beta.kubernetes.io/aws-load-balancer-internal: "true"` → `service.beta.kubernetes.io/azure-load-balancer-internal: "true"`
- **SSL termination:** AWS ACM cert ARN → Azure Application Gateway or cert-manager
- **External DNS:** Verify DNS integration works with Azure DNS

## Annotation Mapping

| EKS | AKS |
|-----|-----|
| `service.beta.kubernetes.io/aws-load-balancer-type: nlb` | Standard LB is default in AKS |
| `service.beta.kubernetes.io/aws-load-balancer-internal: "true"` | `service.beta.kubernetes.io/azure-load-balancer-internal: "true"` |
| `service.beta.kubernetes.io/aws-load-balancer-ssl-cert: <ARN>` | Use AGIC with Application Gateway or cert-manager |
| `service.beta.kubernetes.io/aws-load-balancer-backend-protocol: http` | Not needed — Azure LB handles this natively |

## Gotchas
- AKS uses Azure Standard Load Balancer by default (not Basic)
- Each `LoadBalancer` service gets its own public IP in AKS
- For cost savings, use shared ingress controller instead of per-service LoadBalancers
- AKS internal LB requires subnet with enough IP addresses

## Related
- [[kubernetes_deployment]]
- [[eks-to-aks-manifests]]
