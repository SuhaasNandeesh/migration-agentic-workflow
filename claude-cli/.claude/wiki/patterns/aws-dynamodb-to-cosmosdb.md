# AWS DynamoDB → Azure Cosmos DB

| Source (AWS) | Target (Azure) |
|---|---|
| `aws_dynamodb_table` | `azurerm_cosmosdb_account` + `azurerm_cosmosdb_table` (Table API) OR `azurerm_cosmosdb_sql_container` (Core/SQL API) |
| DynamoDB partition key | Cosmos partition key (`/partitionKey`) — choose a high-cardinality key |
| Provisioned/On-demand capacity | Cosmos `throughput` (manual RU/s) or `autoscale_settings` |
| DynamoDB Streams | Cosmos DB change feed |
| Global Tables | Cosmos multi-region writes (`geo_location` blocks) |

## Golden Example (Table API — closest to DynamoDB)
```hcl
resource "azurerm_cosmosdb_account" "main" {
  name                = "cosmos-${var.app}-${var.environment}"   # 3-44, lowercase, GLOBALLY UNIQUE
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  capabilities { name = "EnableTable" }
  consistency_policy { consistency_level = "Session" }   # DynamoDB-like read-your-writes
  geo_location { location = azurerm_resource_group.main.location; failover_priority = 0 }
  public_network_access_enabled = false
  tags = local.common_tags
}
```

## Gotchas
- **Data model differs** — mark as `functional`/`redesign`, not `direct`. Validate access patterns.
- **RU/s is the cost & throttling unit** — under-provisioning causes 429s; prefer `autoscale_settings { max_throughput = ... }`. See `cosmosdb-request-units` gotcha.
- **Consistency**: `Session` ≈ DynamoDB default; `Strong` only single-region. Don't default to `Strong`.
- Globally-unique account name; data migration is out-of-band (Azure Data Factory / `dt` tool).
