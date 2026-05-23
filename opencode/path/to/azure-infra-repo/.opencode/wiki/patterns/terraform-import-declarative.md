# Terraform 1.5+ Declarative State Import Pattern

Terraform 1.5 introduced the `import` block, which enables state import to be defined declaratively in code rather than imperatively using the CLI command `terraform import`. This allows imports to be peer-reviewed, planned, and executed cleanly as part of the standard CI/CD deployment cycle.

---

## 1. Golden Pattern: Declarative `import` Blocks

When translating stateful AWS resources into their Azure equivalents, the Developer agent must automatically generate an `imports.tf` file alongside the resource definition.

```hcl
# --- imports.tf ---

import {
  to = azurerm_storage_account.data_store
  id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-prod/providers/Microsoft.Storage/storageAccounts/stproddata"
}

import {
  to = azurerm_mssql_database.primary_db
  id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-prod/providers/Microsoft.Sql/servers/sql-prod-srv/databases/db-primary"
}
```

### Key Parameters:
- **`to`**: The local Terraform resource address (type and name) being imported.
- **`id`**: The target cloud resource's platform-specific absolute identifier (for Azure, this is the fully qualified Azure Resource Manager ID).

---

## 2. Dynamic Resource ID Construction

Azure Resource IDs must follow the standard URI format and support dynamic substitution using local environment variables:

```hcl
import {
  to = azurerm_cosmosdb_account.app_nosql
  id = "/subscriptions/${var.azure_subscription_id}/resourceGroups/${var.resource_group_name}/providers/Microsoft.DocumentDB/databaseAccounts/${var.cosmos_account_name}"
}
```

---

## 3. Execution and Auto-Generation Workflow

1. **Write resource code**: Define the resource code without state (e.g. `resource "azurerm_storage_account" "data_store" {}`).
2. **Define the import block**: Generate the `imports.tf` file as shown above.
3. **Run planning with import generation** (Optional):
   Using Terraform 1.5+, you can use the `-generate-config-out` flag to auto-generate the resource configuration if it doesn't already exist:
   ```bash
   terraform plan -generate-config-out=generated_resources.tf
   ```
4. **Apply state addition**:
   ```bash
   terraform apply
   ```
   Terraform will pull the configuration of the remote resource, match it with the `to` reference, and write it into the local state file securely without deleting or recreated the resource.

---

## 4. Architectural Rules for the Migration Factory

- **Target Stateful Only**: Generate imports exclusively for resources carrying persistent state (Databases, KeyVaults, Storage Accounts, CosmosDB, Container Registries). Do NOT generate imports for ephemeral network interfaces, NSG rules, or route tables.
- **Onboarding Controls**: If local dry-runs are required without state binding, set `enable_state_import = false` inside `terraform.tfvars` and guard the `import` blocks using conditional files or instructions where appropriate.
