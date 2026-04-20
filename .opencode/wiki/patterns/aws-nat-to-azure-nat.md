---
pattern: aws-nat-to-azure-nat
complexity: direct
last_updated: "2026-04-19"
source_runs: 1
---
# AWS NAT Gateway to Azure NAT Gateway

## Migration Steps

1. **Replace resource:** `aws_nat_gateway` → `azurerm_nat_gateway`
2. **Replace EIP:** `aws_eip` → `azurerm_public_ip` (Static, Standard)
3. **Associate Public IP:** Create `azurerm_nat_gateway_public_ip_association`
4. **Associate to subnet:** `route_table` in AWS → `azurerm_subnet_nat_gateway_association` in Azure
5. **Add lifecycle protection:** `lifecycle { prevent_destroy = true }`

## Variables to Extract
- `nat_gateway_name`
- Public IP allocation method (always Static for NAT)

## Validation Criteria
- No `aws_nat_gateway` or `aws_eip` references remain
- Public IP is Static + Standard SKU
- NAT is associated to at least one subnet
- Lifecycle prevent_destroy is set

## Related
- [[azurerm_nat_gateway]]
- [[nat-gateway-no-delete-protection]]
