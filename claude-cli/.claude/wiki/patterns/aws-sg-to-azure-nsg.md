---
pattern: aws-sg-to-azure-nsg
complexity: functional
last_updated: "2026-04-19"
source_runs: 1
---
# AWS Security Group to Azure NSG

## Migration Steps

1. **Replace resource:** `aws_security_group` → `azurerm_network_security_group`
2. **Map ingress rules:** `aws_security_group_rule` (type=ingress) → `security_rule` blocks with `direction = "Inbound"`
3. **Map egress rules:** `aws_security_group_rule` (type=egress) → `security_rule` blocks with `direction = "Outbound"`
4. **Add priorities:** Azure NSG rules require `priority` (100-4096) — AWS has no priority concept
5. **Associate to subnet:** Create `azurerm_subnet_network_security_group_association` (AWS attaches to instances)
6. **Explicit egress:** Don't just copy AWS allow-all egress — be explicit about allowed outbound ports

## Priority Assignment Strategy
- SSH/RDP access: 100-199
- Application ports: 200-399
- Database ports: 400-599
- Management ports: 600-799
- Deny rules: 4000-4096

## Gotchas
- Each priority must be UNIQUE per direction
- Don't forget to add EGRESS rules — AWS often has blanket allow-all outbound
- NSG can attach to subnet OR NIC — prefer subnet-level for consistency

## Validation Criteria
- No `aws_security_group` references remain
- Every rule has a unique priority
- Egress rules are explicit (not just allow-all)
- NSG is associated to at least one subnet

## Related
- [[azurerm_network_security_group]]
