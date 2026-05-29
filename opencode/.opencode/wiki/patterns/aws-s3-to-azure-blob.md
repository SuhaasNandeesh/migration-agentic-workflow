# AWS S3 → Azure Blob Storage

| Source (AWS) | Target (Azure) |
|---|---|
| `aws_s3_bucket` | `azurerm_storage_account` + `azurerm_storage_container` |
| `aws_s3_bucket_versioning` | `blob_properties { versioning_enabled = true }` on the account |
| `aws_s3_bucket_server_side_encryption_configuration` | encryption is on by default (Microsoft-managed) or `customer_managed_key` (CMK via Key Vault) |
| `aws_s3_bucket_lifecycle_configuration` | `azurerm_storage_management_policy` |
| `aws_s3_bucket_public_access_block` | `public_network_access_enabled = false` + `allow_nested_items_to_be_public = false` |

## Golden Example
```hcl
resource "azurerm_storage_account" "data" {
  name                            = "st${var.app}${var.environment}"   # 3-24, lowercase alnum ONLY, GLOBALLY UNIQUE
  resource_group_name             = azurerm_resource_group.main.name
  location                        = azurerm_resource_group.main.location
  account_tier                    = "Standard"
  account_replication_type        = var.environment == "prod" ? "GRS" : "LRS"
  min_tls_version                 = "TLS1_2"
  public_network_access_enabled   = false
  allow_nested_items_to_be_public = false
  blob_properties { versioning_enabled = true }
  tags = local.common_tags
}

resource "azurerm_storage_container" "main" {
  name                  = "data"
  storage_account_id    = azurerm_storage_account.data.id
  container_access_type = "private"
}
```

## Gotchas
- **Name = 3–24 chars, lowercase letters+digits ONLY, globally unique** — hyphens/underscores are INVALID. Run `azure-naming-validator`.
- **One bucket ≠ one account.** Many small S3 buckets should map to *containers* within a few storage accounts (Azure caps ~250 accounts/region/subscription).
- **Object data is NOT copied by IaC** — use `azcopy`/AWS DataSync separately.
- Map `GRS`/`ZRS`/`LRS` from the source durability/replication intent; default prod → `GRS`.
