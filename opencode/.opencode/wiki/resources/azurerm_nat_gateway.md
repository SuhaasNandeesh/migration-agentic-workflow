---
resource: azurerm_nat_gateway
provider: azurerm
aws_equivalent: aws_nat_gateway
last_updated: "2026-04-19"
source_runs: 1
---
# azurerm_nat_gateway

## Overview
Azure NAT Gateway. Replaces AWS NAT Gateway + EIP.

## Key Differences

| Aspect | AWS | Azure |
|--------|-----|-------|
| EIP required | `aws_eip` separate | `azurerm_public_ip` + `azurerm_nat_gateway_public_ip_association` |
| Subnet association | Created IN a subnet | Associated TO a subnet via `azurerm_subnet_nat_gateway_association` |
| Deletion protection | Implicit (can't delete if in use) | No built-in — add `lifecycle { prevent_destroy = true }` |

## Gotchas
- [[nat-gateway-no-delete-protection]] — Azure NAT has no implicit deletion protection
- NAT must be defined in ONE module only — avoid duplication between network and nat modules
- Public IP for NAT should be `Static` allocation with `Standard` SKU

## Related
- [[azurerm_public_ip]] — Required companion
- [[azurerm_virtual_network]] — Parent network
