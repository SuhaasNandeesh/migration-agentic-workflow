# AWS RDS → Azure Database Flexible Server

| Source (AWS) | Target (Azure) |
|---|---|
| `aws_db_instance` (MySQL) | `azurerm_mysql_flexible_server` (+ `azurerm_mysql_flexible_database`) |
| `aws_db_instance` (PostgreSQL) | `azurerm_postgresql_flexible_server` (+ `azurerm_postgresql_flexible_server_database`) |
| `aws_db_instance` (SQL Server) | `azurerm_mssql_server` + `azurerm_mssql_database` |
| `aws_rds_cluster` (Aurora MySQL/PG) | flexible server (no Aurora equivalent — redesign to single/HA flexible server) |
| `aws_db_subnet_group` | delegated subnet + `azurerm_private_dns_zone` (VNet integration) |

## Golden Example (PostgreSQL)
```hcl
resource "azurerm_postgresql_flexible_server" "main" {
  name                = "psql-${var.app}-${var.environment}"   # 3-63, lowercase, GLOBALLY UNIQUE
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  version             = "16"
  sku_name            = var.environment == "prod" ? "GP_Standard_D2ds_v5" : "B_Standard_B1ms"
  storage_mb          = 32768
  zone                = "1"
  high_availability { mode = var.environment == "prod" ? "ZoneRedundant" : "Disabled" }
  # Private access: integrate into a delegated subnet + private DNS zone, no public endpoint.
  delegated_subnet_id = azurerm_subnet.db.id
  private_dns_zone_id = azurerm_private_dns_zone.psql.id
  administrator_login    = var.db_admin_user
  administrator_password = var.db_admin_password   # from Key Vault, never hardcoded
  tags = local.common_tags
}
```

## Gotchas
- **No Multi-AZ flag** — use `high_availability { mode = "ZoneRedundant" }` (prod only; costs ~2x).
- **Public access off** — set VNet integration (`delegated_subnet_id` + `private_dns_zone_id`); do NOT expose a public endpoint.
- **Engine version strings differ** (e.g. `"16"` not `"16.1"` for PG flexible server).
- **Data is NOT migrated by IaC** — use Azure DMS / `pg_dump`/`mysqldump` separately; IaC only provisions the server. Generate `imports.tf` only if the target already exists.
- Credentials → Key Vault references; never inline.
