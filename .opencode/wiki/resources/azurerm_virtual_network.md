---
resource: azurerm_virtual_network
provider: azurerm
aws_equivalent: aws_vpc
last_updated: "2026-04-19"
source_runs: 1
---
# azurerm_virtual_network

## Overview
Azure Virtual Network. Replaces AWS VPC `aws_vpc`.

## Key Differences from AWS VPC

| Aspect | AWS (`aws_vpc`) | Azure (`azurerm_virtual_network`) |
|--------|----------------|----------------------------------|
| CIDR | `cidr_block` (single) | `address_space` (list — supports multiple) |
| Internet Gateway | Separate `aws_internet_gateway` resource | Built-in (no separate resource needed) |
| DNS | `enable_dns_support`, `enable_dns_hostnames` | Azure DNS is automatic |
| Resource Group | N/A (AWS uses regions) | `resource_group_name` required |
| Location | Region in provider config | `location` on resource |

## Required Variables
- `vnet_name` — VNet name (follow `vnet-<project>-<env>-<region>` pattern)
- `address_space` — CIDR blocks (list of strings, validate with `can(cidrhost())`)
- `location` — Azure region
- `resource_group_name` — Target resource group

## Gotchas
- Azure VNet supports MULTIPLE address spaces — can add secondary CIDRs
- No separate internet gateway needed — Azure VNets have implicit internet routing
- DNS resolution is automatic — no `enable_dns_support` equivalent
- Subnets in Azure are child resources, not separate resources like AWS

## Related
- [[azurerm_subnet]] — Subnets within VNet
- [[azurerm_route_table]] — Custom routing
- [[aws-vpc-to-azure-vnet]] — Full migration pattern
