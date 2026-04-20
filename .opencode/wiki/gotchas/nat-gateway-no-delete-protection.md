---
id: nat-gateway-no-delete-protection
severity: medium
discovered_in_run: 1
last_updated: "2026-04-19"
---
# Azure NAT Gateway Has No Implicit Deletion Protection

## Problem
AWS NAT Gateway has implicit deletion protection (can't delete if subnets depend on it). Azure NAT Gateway has no such protection — it can be accidentally destroyed.

## Fix
Add lifecycle rule for production NAT Gateways:
```hcl
resource "azurerm_nat_gateway" "main" {
  # ...config...
  lifecycle {
    prevent_destroy = true
  }
}
```

## Related
- [[azurerm_nat_gateway]]
