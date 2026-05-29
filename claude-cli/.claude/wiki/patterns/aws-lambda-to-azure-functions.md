# AWS Lambda → Azure Functions

| Source (AWS) | Target (Azure) |
|---|---|
| `aws_lambda_function` | `azurerm_linux_function_app` (+ `azurerm_service_plan`) |
| `aws_lambda_function` (Windows) | `azurerm_windows_function_app` |
| Lambda needs a storage backend | `azurerm_storage_account` (required by Functions runtime) |
| `aws_lambda_permission` / triggers | binding-specific (Event Grid, Service Bus, HTTP, Timer) |
| Provisioned concurrency | `service_plan` SKU (EP elastic premium) |

## Golden Example
```hcl
resource "azurerm_service_plan" "fn" {
  name                = "asp-${var.app}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = var.environment == "prod" ? "EP1" : "Y1"   # Y1 = consumption
}

resource "azurerm_linux_function_app" "fn" {
  name                       = "func-${var.app}-${var.environment}"   # 2-60, GLOBALLY UNIQUE
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  service_plan_id            = azurerm_service_plan.fn.id
  storage_account_name       = azurerm_storage_account.fn.name
  storage_account_access_key = azurerm_storage_account.fn.primary_access_key
  identity { type = "SystemAssigned" }              # use Managed Identity, not keys
  site_config { application_stack { python_version = "3.11" } }
  tags = local.common_tags
}
```

## Gotchas
- **A storage account is mandatory** for the Functions runtime — always provision one.
- **Runtime handler signature differs** — code changes are required; mark `functional`/`redesign`, not `direct`.
- Map Lambda triggers to **bindings**: SQS→Service Bus trigger, SNS/EventBridge→Event Grid trigger, API Gateway→HTTP trigger, CloudWatch Events→Timer trigger.
- Consumption plan = `Y1`; Premium (no cold start, VNet) = `EP1`+.
