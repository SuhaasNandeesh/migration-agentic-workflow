# Kubernetes Migration Patterns (Examples)

> These are EXAMPLE patterns. Handle any K8s annotation, storage class, or controller not listed using training knowledge.

## Annotations

| Source Platform Annotation | Target Platform (AKS) | Notes |
|---------------------------|----------------------|-------|
| `eks.amazonaws.com/role-arn` | `azure.workload.identity/client-id` | Also add `azure.workload.identity/use: "true"` label |
| `iam.gke.io/gcp-service-account` | `azure.workload.identity/client-id` | Same Workload Identity pattern |
| `service.beta.kubernetes.io/aws-load-balancer-type: nlb` | `service.beta.kubernetes.io/azure-load-balancer-internal: "true"` | Azure LB config |
| `kubernetes.io/ingress.class: alb` | `kubernetes.io/ingress.class: azure/application-gateway` | Or NGINX ingress |
| `alb.ingress.kubernetes.io/*` | `appgw.ingress.kubernetes.io/*` | AGIC annotations |

## Storage Classes

| Source CSI Driver | Target CSI Driver (AKS) | Notes |
|------------------|------------------------|-------|
| `ebs.csi.aws.com` | `disk.csi.azure.com` | Azure Managed Disks |
| `efs.csi.aws.com` | `file.csi.azure.com` | Azure Files |
| `pd.csi.storage.gke.io` | `disk.csi.azure.com` | |
| `s3.csi.aws.com` | `blob.csi.azure.com` | Azure Blob NFS |

## Container Registries

| Source Registry Pattern | Target Registry (Azure) |
|------------------------|------------------------|
| `*.dkr.ecr.*.amazonaws.com/<repo>` | `<registry>.azurecr.io/<repo>` |
| `gcr.io/<project>/<repo>` | `<registry>.azurecr.io/<repo>` |
| `docker.io/<repo>` | Keep as-is or mirror to ACR |

## Identity Mechanisms

| Source | Target (AKS) | Migration Steps |
|--------|--------------|----------------|
| AWS IRSA | Azure Workload Identity | 1. Create Managed Identity 2. Create Federated Credential 3. Update SA annotation |
| GKE Workload Identity | Azure Workload Identity | Similar pattern, different annotation |
| Static secrets in K8s Secret | Azure Key Vault + CSI driver | Use `secrets-store.csi.k8s.io` |

## Controllers & Operators

| Source | Target (AKS) | Notes |
|--------|--------------|-------|
| AWS Load Balancer Controller | AGIC or NGINX Ingress Controller | Depends on use case |
| AWS EFS CSI Driver | Azure Files CSI Driver | Built into AKS |
| External DNS (AWS Route53) | External DNS (Azure DNS) | Change provider config |
| Cluster Autoscaler (AWS ASG) | KEDA or AKS built-in autoscaler | AKS has native autoscaling |

## General Rules
- Remove ALL source platform annotations
- Replace ALL source CSI drivers with target equivalents
- Update ALL image references to target container registry
- Replace ALL identity mechanisms with target equivalent
- Any custom operator → check if target platform has equivalent or keep as-is
