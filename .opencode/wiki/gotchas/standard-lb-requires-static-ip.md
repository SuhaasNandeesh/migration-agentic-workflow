---
id: standard-lb-requires-static-ip
severity: high
discovered_in_run: 1
last_updated: "2026-04-19"
---
# Standard Load Balancer Requires Static Public IP

## Problem
Azure Standard Load Balancer requires a Standard SKU Public IP with Static allocation. Using `Dynamic` allocation or Basic SKU causes deployment failures.

## Fix
```hcl
resource "azurerm_public_ip" "lb" {
  name                = "${var.project_name}-lb-pip"
  allocation_method   = "Static"    # NOT "Dynamic"
  sku                 = "Standard"  # Must match LB SKU
}

resource "azurerm_lb" "main" {
  sku = "Standard"  # ALWAYS Standard — Basic is deprecated
}
```

## Related
- [[azurerm_lb]]
- [[dynamic-vs-static-public-ip]]
