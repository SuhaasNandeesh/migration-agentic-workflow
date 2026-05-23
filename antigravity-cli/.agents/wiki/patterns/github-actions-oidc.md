# Golden Pattern: GitHub Actions to Azure OIDC Authentication

Eliminate long-lived secrets (`AZURE_CLIENT_SECRET`) from your CI/CD pipelines. This pattern uses OpenID Connect (OIDC) to establish a trusted relationship between GitHub Actions and Microsoft Entra ID. GitHub requests temporary credentials dynamically during the runner's execution phase.

---

## 1. Terraform Federated Trust Credential

To allow GitHub Actions to authenticating without a client secret, you must provision a User-Assigned Managed Identity and establish a federated credential representing the GitHub workflow.

```hcl
# 1. User-Assigned Managed Identity for the Pipeline Runner
resource "azurerm_user_assigned_identity" "pipeline_runner" {
  name                = "uami-github-runner-${var.environment}"
  resource_group_name = var.resource_group_name
  location            = var.location
}

# 2. Grant Subscription Contributor Permissions
resource "azurerm_role_assignment" "runner_contributor" {
  scope                = "/subscriptions/${var.subscription_id}"
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.pipeline_runner.principal_id
}

# 3. Create Federated Credential for GitHub Environment
resource "azurerm_federated_identity_credential" "github_oidc" {
  name                = "fed-cred-github-${var.environment}"
  resource_group_name = var.resource_group_name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  
  # Limit trust specifically to your repo's environment
  # Subject format: repo:<org>/<repo>:environment:<env-name>
  subject             = "repo:${var.github_org}/${var.github_repo}:environment:${var.environment}"
}
```

---

## 2. GitHub Actions Workflow Skeleton

The GitHub Actions workflow must be granted explicit permissions to request the OIDC JWT token (`id-token: write`). We configure the AzureRM provider to consume these credentials dynamically.

```yaml
name: "Terraform Multi-Environment Deployment"

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

permissions:
  id-token: write # REQUIRED: Allows requesting the JWT OIDC token
  contents: read  # REQUIRED: Allows checking out the repository code

jobs:
  deploy:
    name: "Deploy Environment"
    runs-on: ubuntu-latest
    environment: production # Binds to the federated subject environment name

    variables:
      AZURE_CLIENT_ID: "00000000-0000-0000-0000-000000000000" # Managed Identity Client ID
      AZURE_TENANT_ID: "00000000-0000-0000-0000-000000000000" # Entra ID Tenant ID
      AZURE_SUBSCRIPTION_ID: "00000000-0000-0000-0000-000000000000" # Target Subscription ID

    steps:
      - name: "Checkout Code"
        uses: actions/checkout@v4

      - name: "Setup Terraform"
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.11.0"

      - name: "Terraform Plan & Apply"
        env:
          ARM_USE_OIDC: "true"
          ARM_CLIENT_ID: ${{ vars.AZURE_CLIENT_ID }}
          ARM_TENANT_ID: ${{ vars.AZURE_TENANT_ID }}
          ARM_SUBSCRIPTION_ID: ${{ vars.AZURE_SUBSCRIPTION_ID }}
        run: |
          terraform init -backend-config="storage_account_name=sttfstateproduction" \
                         -backend-config="container_name=tfstate" \
                         -backend-config="key=infra.tfstate"
          terraform plan -out=tfplan
          terraform apply -auto-approve tfplan
```

---

## 3. Production Rules & Fallback (Zero-Trust Resilience)

* **OIDC Fallback Support:** In environments where OIDC is restricted or blocked due to organizational proxy controls, the code must dynamically fall back to standard Service Principal secrets. This is handled by configuring the provider using:
  ```hcl
  provider "azurerm" {
    features {}
    use_oidc = var.use_oidc_auth # Set to false if using static credentials
  }
  ```
* **Strict Environments Pinning:** Never use wildcard subjects like `repo:<org>/<repo>:*` in production credentials, as any developer committing a change to a personal feature branch could trigger deployment permissions to production.
