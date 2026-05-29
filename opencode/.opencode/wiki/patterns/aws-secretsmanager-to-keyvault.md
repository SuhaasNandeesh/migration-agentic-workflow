# AWS Secrets/Config/KMS → Azure Key Vault

| Source (AWS) | Target (Azure) |
|---|---|
| `aws_secretsmanager_secret` (+ `_version`) | `azurerm_key_vault_secret` |
| `aws_ssm_parameter` (SecureString) | `azurerm_key_vault_secret` |
| `aws_ssm_parameter` (String/plain config) | `azurerm_app_configuration_key` (App Configuration) or Key Vault |
| `aws_kms_key` / `aws_kms_alias` | `azurerm_key_vault_key` (+ `azurerm_disk_encryption_set` for disk CMK) |

## Golden Example
```hcl
resource "azurerm_key_vault" "main" {
  name                       = "kv-${var.app}-${var.environment}"   # 3-24, alnum+hyphen, GLOBALLY UNIQUE
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = true     # see keyvault-soft-delete-purge gotcha
  soft_delete_retention_days = 90
  enable_rbac_authorization  = true     # prefer RBAC over access policies
  public_network_access_enabled = false
}

resource "azurerm_key_vault_secret" "db" {
  name         = "db-password"
  value        = var.db_password           # supplied at apply, never committed
  key_vault_id = azurerm_key_vault.main.id
}
```

## Rewriting references (CRITICAL)
- App code / pipelines that read `secretsmanager:GetSecretValue` or `ssm:GetParameter` MUST be rewritten to Key Vault references (CSI driver `SecretProviderClass` for AKS, `@Microsoft.KeyVault(...)` for App Service, or SDK calls with Managed Identity).
- Grant access via **Managed Identity + RBAC role** (`Key Vault Secrets User`), never static credentials.

## Gotchas
- **Globally-unique vault name**; soft-delete is always on and `purge_protection_enabled = true` means a destroyed vault name is reserved ~90 days (blocks re-creation with the same name).
- Secret *values* are not migrated by IaC — re-seed them via pipeline/Managed Identity, do not commit.
