---
resource: azurerm_lb
provider: azurerm
aws_equivalent: aws_lb
last_updated: "2026-04-19"
source_runs: 1
---
# azurerm_lb

## Overview
Azure Load Balancer. Replaces AWS ELB/ALB/NLB.

## Key Differences

| Aspect | AWS (`aws_lb`) | Azure (`azurerm_lb`) |
|--------|---------------|---------------------|
| SKU | Standard (default) | MUST specify `sku = "Standard"` (Basic is deprecated) |
| Target groups | `aws_lb_target_group` | `azurerm_lb_backend_address_pool` |
| Listeners | `aws_lb_listener` | `azurerm_lb_rule` |
| Health checks | Part of target group | Separate `azurerm_lb_probe` resource |
| Public IP | Created with LB | Separate `azurerm_public_ip` (MUST be Static + Standard SKU) |

## Gotchas
- **ALWAYS set `sku = "Standard"`** — Basic SKU is being retired by Azure
- **Public IP must match LB SKU** — Standard LB requires Standard Public IP with Static allocation
- Backend pool is EMPTY by default — must associate VM NICs via `azurerm_network_interface_backend_address_pool_association`
- Health probe is a SEPARATE resource — don't forget to create it
- `azurerm_lb_rule` requires `probe_id` — link the health probe

## Related
- [[aws-elb-to-azure-lb]] — Migration pattern
- [[azurerm_public_ip]] — Required for public LB
- [[standard-lb-requires-static-ip]] — Common gotcha
