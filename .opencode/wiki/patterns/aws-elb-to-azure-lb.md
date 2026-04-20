---
pattern: aws-elb-to-azure-lb
complexity: functional
last_updated: "2026-04-19"
source_runs: 1
---
# AWS ELB/ALB to Azure Load Balancer

## Migration Steps

1. **Replace resource:** `aws_lb` → `azurerm_lb`
2. **Set SKU:** ALWAYS set `sku = "Standard"` (Basic is deprecated)
3. **Create Public IP:** `azurerm_public_ip` with `allocation_method = "Static"`, `sku = "Standard"`
4. **Map target group:** `aws_lb_target_group` → `azurerm_lb_backend_address_pool`
5. **Map listener:** `aws_lb_listener` → `azurerm_lb_rule`
6. **Map health check:** Part of target group in AWS → separate `azurerm_lb_probe` in Azure
7. **Map target attachment:** `aws_lb_target_group_attachment` → `azurerm_network_interface_backend_address_pool_association`

## Companion Resources (must ALL be created)
- `azurerm_public_ip` (Static, Standard SKU)
- `azurerm_lb` (Standard SKU)
- `azurerm_lb_backend_address_pool`
- `azurerm_lb_probe`
- `azurerm_lb_rule` (links probe + backend pool)
- `azurerm_network_interface_backend_address_pool_association` (links VMs)

## Validation Criteria
- No `aws_lb*` references remain
- LB uses Standard SKU
- Public IP matches LB SKU (Standard + Static)
- Health probe exists and is linked to LB rule
- Backend pool has NIC associations

## Related
- [[azurerm_lb]]
- [[standard-lb-requires-static-ip]]
