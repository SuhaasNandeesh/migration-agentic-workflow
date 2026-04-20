---
id: dynamic-vs-static-public-ip
severity: medium
discovered_in_run: 1
last_updated: "2026-04-19"
---
# Dynamic vs Static Public IP Allocation

## Problem
AWS Elastic IPs are always static. Azure Public IPs can be `Dynamic` or `Static`. Using `Dynamic` means the IP changes on VM restart, and Standard LBs reject Dynamic IPs entirely.

## When to Use Each
| Use Case | Allocation | SKU |
|----------|-----------|-----|
| Load Balancer frontend | `Static` | `Standard` |
| NAT Gateway | `Static` | `Standard` |
| Production VM (needs stable IP) | `Static` | `Standard` |
| Dev/test VM (IP doesn't matter) | `Dynamic` | `Basic` |

## Fix
Always default to Static for migrated EIPs:
```hcl
variable "ip_allocation_method" {
  type        = string
  default     = "Static"
  description = "Public IP allocation method"
  validation {
    condition     = contains(["Static", "Dynamic"], var.ip_allocation_method)
    error_message = "Must be Static or Dynamic."
  }
}
```

## Related
- [[azurerm_lb]] — Requires Static
- [[azurerm_nat_gateway]] — Requires Static
