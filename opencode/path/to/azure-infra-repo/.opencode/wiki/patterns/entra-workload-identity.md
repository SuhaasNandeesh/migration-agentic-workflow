# Golden Pattern: Microsoft Entra Workload Identity

**Microsoft Entra Workload Identity** replaces the deprecated AAD Pod Identity mechanism. It utilizes OIDC federation to allow Kubernetes pods to authenticate directly against Azure resources (such as Azure Key Vault, CosmosDB, or Storage Accounts) using temporary service account tokens, eliminating the need for long-lived client secrets.

---

## 1. Terraform Infrastructure Provisioning

To enable Workload Identity, you must provision:
1. A **User-Assigned Managed Identity (UAMI)** in Azure.
2. A **Federated Identity Credential** linking the UAMI to your AKS cluster's OIDC issuer URL.
3. Relevant Azure RBAC role assignments.

```hcl
# 1. Create User-Assigned Managed Identity
resource "azurerm_user_assigned_identity" "workload_identity" {
  name                = "uami-service-auth-${var.environment}"
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags
}

# 2. Grant permissions to User-Assigned Managed Identity (e.g. Reader)
resource "azurerm_role_assignment" "kv_reader" {
  scope                = var.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.workload_identity.principal_id
}

# 3. Establish Trust Federated Identity Credential
resource "azurerm_federated_identity_credential" "aks_federation" {
  name                = "fed-cred-aks-${var.environment}"
  resource_group_name = var.resource_group_name
  audience            = ["api://AzureADTokenExchange"]
  
  # The OIDC issuer URL returned by the AKS cluster
  issuer              = var.aks_oidc_issuer_url
  
  # Kubernetes Service Account: "system:serviceaccount:<namespace>:<service-account-name>"
  subject             = "system:serviceaccount:${var.k8s_namespace}:${var.k8s_service_account_name}"
}
```

---

## 2. Kubernetes Resource Configuration

The Kubernetes deployment must define an annotated Service Account and instruct the pod to use it. The Azure admission controller will automatically inject environment variables (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_FEDERATED_TOKEN_FILE`) and mount the projected token.

### Service Account Manifest (`service-account.yaml`)
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-service-sa
  namespace: production
  annotations:
    # Binds the Kubernetes SA to the Azure Managed Identity Client ID
    azure.workload.identity/client-id: "00000000-0000-0000-0000-000000000000" # Replace with UAMI Client ID
```

### Deployment Manifest (`deployment.yaml`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-worker
  namespace: production
  labels:
    app: app-worker
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app-worker
  template:
    metadata:
      labels:
        app: app-worker
        # MUST be labeled to instruct the webhook to inject credentials
        azure.workload.identity/use: "true"
    spec:
      serviceAccountName: app-service-sa
      containers:
      - name: worker
        image: acrproduction.azurecr.io/worker:v1.2.0
        ports:
        - containerPort: 80
```

---

## 3. Production Rules & Gotchas

* **Correct Subject Matching:** The federated credential subject `system:serviceaccount:<namespace>:<service-account-name>` is case-sensitive and must **exactly match** the Kubernetes manifest values.
* **Webhook Dependency:** Ensure that `workload_identity_enabled = true` is configured in your `azurerm_kubernetes_cluster` resource, as Azure will not launch the mutating admission webhook otherwise.
* **OIDC Cache Lag:** When creating a new Federated Identity Credential, it may take up to 60 seconds for Microsoft Entra ID to propagate the federation token trust, causing initial pod starts to fail authentication. Program robust retries into application boot scripts.
