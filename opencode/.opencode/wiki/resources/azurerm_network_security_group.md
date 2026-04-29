---
resource: azurerm_network_security_group
provider: azurerm
aws_equivalent: aws_security_group
last_updated: "2026-04-19"
source_runs: 1
---
# azurerm_network_security_group

## Overview
Azure Network Security Group (NSG). Replaces AWS Security Group.

## Key Differences from AWS SG

| Aspect | AWS (`aws_security_group`) | Azure (`azurerm_network_security_group`) |
|--------|--------------------------|----------------------------------------|
| Default behavior | Deny all inbound, allow all outbound | Same, but explicit rules recommended |
| Rule priority | No priority (evaluate all rules) | `priority` field required (100-4096, lower = higher priority) |
| Rule definition | Separate `aws_security_group_rule` resources | Inline `security_rule` blocks OR separate `azurerm_network_security_rule` |
| Association | Attached to instance/ENI | Attached to subnet OR NIC via `azurerm_subnet_network_security_group_association` |
| Stateful | Fully stateful | Stateful (return traffic auto-allowed) |

## Required Variables
- `nsg_name` — NSG name
- `allowed_ports` — Map or list of port rules to create

## Gotchas
- **Egress rules matter!** AWS often has `0.0.0.0/0` allow-all egress. In Azure, be explicit about which ports are allowed outbound — don't just copy with `Allow-All-Outbound`
- Priority values must be UNIQUE per direction (inbound/outbound)
- Ports 3389 (RDP), 8080 (HTTP-alt) are commonly forgotten during migration
- NSG can be associated to BOTH subnets AND NICs — subnet-level is recommended for consistency
- Use `azurerm_network_security_rule` as separate resources for dynamic rule sets

## Related
- [[aws-sg-to-azure-nsg]] — Full migration pattern
- [[azurerm_virtual_network]] — Parent network
