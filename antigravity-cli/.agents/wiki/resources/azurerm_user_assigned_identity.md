---
resource: azurerm_user_assigned_identity
provider: azurerm
aws_equivalent: aws_iam_role + aws_iam_instance_profile
last_updated: "2026-04-19"
source_runs: 1
---
# azurerm_user_assigned_identity

## Overview
Azure Managed Identity. Replaces AWS IAM Role + Instance Profile.

## Key Differences

| Aspect | AWS | Azure |
|--------|-----|-------|
| Role creation | `aws_iam_role` with trust policy | `azurerm_user_assigned_identity` (no trust policy needed) |
| Instance attachment | `aws_iam_instance_profile` | VM `identity { type = "UserAssigned" }` block |
| Policy attachment | `aws_iam_role_policy_attachment` | `azurerm_role_assignment` with RBAC role |
| Scope | Account-wide | Scoped to resource group / subscription / resource |

## Gotchas
- No instance profile needed — Azure MSI is native to VMs
- Role assignments need `scope` — use `var.resource_group_id` for RG-level
- Use least-privilege RBAC roles, not broad roles like `Contributor`
- `principal_id` comes from the identity, not the VM

## Related
- [[aws-iam-to-azure-msi]] — Migration pattern
- [[azurerm_linux_virtual_machine]] — Where identity is attached
