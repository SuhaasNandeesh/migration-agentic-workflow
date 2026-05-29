# AWS CloudWatch → Azure Monitor

| Source (AWS) | Target (Azure) |
|---|---|
| `aws_cloudwatch_log_group` | `azurerm_log_analytics_workspace` (+ diagnostic settings) |
| `aws_cloudwatch_metric_alarm` | `azurerm_monitor_metric_alert` |
| `aws_cloudwatch_dashboard` | `azurerm_portal_dashboard` (or Azure Monitor Workbook) |
| log/metric routing to a resource | `azurerm_monitor_diagnostic_setting` (attach to each resource) |
| SNS alarm action | `azurerm_monitor_action_group` |

## Golden Example
```hcl
resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${var.app}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = var.environment == "prod" ? 90 : 30
  tags                = local.common_tags
}

resource "azurerm_monitor_action_group" "ops" {
  name                = "ag-ops-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  short_name          = "ops"
  email_receiver { name = "oncall"; email_address = var.oncall_email }
}

resource "azurerm_monitor_metric_alert" "cpu" {
  name                = "alert-high-cpu-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_linux_virtual_machine.web.id]
  criteria { metric_namespace = "Microsoft.Compute/virtualMachines"; metric_name = "Percentage CPU"; aggregation = "Average"; operator = "GreaterThan"; threshold = 80 }
  action { action_group_id = azurerm_monitor_action_group.ops.id }
}
```

## Gotchas
- **Diagnostic settings are per-resource** — you must attach `azurerm_monitor_diagnostic_setting` to each resource you want logs/metrics from (no implicit global capture like CloudWatch).
- Alarm SNS actions → `azurerm_monitor_action_group` (email/webhook/SMS/Logic App).
- Metric names/namespaces differ from CloudWatch — map intent, not literal names.
