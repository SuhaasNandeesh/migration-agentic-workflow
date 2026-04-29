---
pattern: aws-vpc-to-azure-vnet
complexity: direct
last_updated: "2026-04-19"
source_runs: 1
---
# AWS VPC to Azure Virtual Network

## Migration Steps

1. **Replace resource:** `aws_vpc` → `azurerm_virtual_network`
2. **Map CIDR:** `cidr_block` → `address_space` (note: Azure supports multiple address spaces)
3. **Remove IGW:** Azure VNets have implicit internet routing — no `aws_internet_gateway` needed
4. **Map subnets:** `aws_subnet` → `azurerm_subnet` (note: subnets are child resources in Azure)
5. **Map route tables:** `aws_route_table` → `azurerm_route_table`
6. **Remove DNS config:** Azure DNS is automatic — no `enable_dns_support` equivalent
7. **Add resource group:** Every Azure resource needs `resource_group_name`

## Variables to Extract
- `vnet_name` (follow `vnet-<project>-<env>-<region>` pattern)
- `address_space` (list of CIDRs)
- `location` (Azure region)
- `resource_group_name`

## Validation Criteria
- No `aws_vpc` references remain
- No `aws_internet_gateway` (not needed in Azure)
- Subnets use correct CIDR ranges within VNet address space
- Resource group is referenced, not hardcoded

## Related
- [[azurerm_virtual_network]]
- [[azurerm_subnet]]
