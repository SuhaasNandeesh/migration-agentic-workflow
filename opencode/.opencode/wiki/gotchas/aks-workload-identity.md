---
id: aks-workload-identity
severity: high
last_updated: "2026-04-22"
source_runs: 0
---
# AKS Workload Identity Replaces IRSA

## Problem
AWS EKS uses IRSA (IAM Roles for Service Accounts) for pod-level IAM:
```yaml
# EKS — IRSA annotation
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/my-role
```

This annotation has NO meaning in AKS. Pods will lose all cloud permissions after migration.

## Fix
Use Azure Workload Identity (the AKS equivalent of IRSA):
```yaml
# AKS — Workload Identity annotation
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    azure.workload.identity/client-id: "<managed-identity-client-id>"
  labels:
    azure.workload.identity/use: "true"
```

Additionally, the Deployment must have the label:
```yaml
spec:
  template:
    metadata:
      labels:
        azure.workload.identity/use: "true"
```

## Terraform Setup Required
```hcl
resource "azurerm_user_assigned_identity" "workload" {
  name                = "id-${var.app_name}-${var.environment}"
  resource_group_name = var.resource_group_name
  location            = var.location
}

resource "azurerm_federated_identity_credential" "workload" {
  name                = "fed-${var.app_name}"
  resource_group_name = var.resource_group_name
  parent_id           = azurerm_user_assigned_identity.workload.id
  audience            = ["api://AzureADTokenExchange"]
  issuer              = azurerm_kubernetes_cluster.main.oidc_issuer_url
  subject             = "system:serviceaccount:${var.namespace}:${var.service_account_name}"
}
```

## Detection Pattern
```bash
grep -rn "eks.amazonaws.com/role-arn" --include="*.yaml" --include="*.yml"
```

## Related
- [[kubernetes_deployment]]
- [[eks-to-aks-manifests]]
