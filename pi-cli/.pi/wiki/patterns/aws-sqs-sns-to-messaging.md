# AWS SQS / SNS / EventBridge → Azure Messaging

| Source (AWS) | Target (Azure) | Notes |
|---|---|---|
| `aws_sqs_queue` | `azurerm_servicebus_queue` (in a `azurerm_servicebus_namespace`) | Standard tier; Premium for VNet/high throughput |
| `aws_sqs_queue` (simple, high-volume) | `azurerm_storage_queue` | cheaper, fewer features (no dead-letter, sessions) |
| `aws_sns_topic` (+ subscriptions) | `azurerm_servicebus_topic` + `azurerm_servicebus_subscription` (pub/sub) | |
| `aws_sns_topic` (event fan-out) | `azurerm_eventgrid_topic` + `azurerm_eventgrid_event_subscription` | event-driven |
| `aws_cloudwatch_event_rule` (EventBridge) | `azurerm_eventgrid_system_topic` + subscription | |

## Golden Example (SQS → Service Bus queue)
```hcl
resource "azurerm_servicebus_namespace" "main" {
  name                = "sb-${var.app}-${var.environment}"   # 6-50, start with letter, GLOBALLY UNIQUE
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = var.environment == "prod" ? "Premium" : "Standard"
  tags                = local.common_tags
}

resource "azurerm_servicebus_queue" "orders" {
  name                                 = "orders"
  namespace_id                         = azurerm_servicebus_namespace.main.id
  dead_lettering_on_message_expiration = true            # SQS DLQ equivalent
  max_delivery_count                   = 10              # SQS maxReceiveCount
  lock_duration                        = "PT30S"         # SQS visibility timeout
}
```

## Gotchas
- **Visibility timeout → `lock_duration`**; **maxReceiveCount → `max_delivery_count`** + `dead_lettering_on_message_expiration`.
- SNS fan-out → choose **Service Bus topic** (ordered, sessions) vs **Event Grid** (lightweight event routing) based on intent.
- FIFO queues → Service Bus **sessions** (`requires_session = true`), not Storage queues.
- Producers/consumers authenticate via **Managed Identity** (RBAC `Azure Service Bus Data Sender/Receiver`), not connection strings.
