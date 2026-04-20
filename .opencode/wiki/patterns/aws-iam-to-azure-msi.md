---
pattern: aws-iam-to-azure-msi
complexity: functional
last_updated: "2026-04-19"
source_runs: 1
---
# AWS IAM to Azure Managed Identity

## Migration Steps

1. **Replace IAM Role:** `aws_iam_role` → `azurerm_user_assigned_identity`
2. **Remove trust policy:** Azure MSI doesn't need trust policies — identity is scoped to resource group
3. **Remove instance profile:** `aws_iam_instance_profile` → not needed (Azure MSI is native)
4. **Map policy attachment:** `aws_iam_role_policy_attachment` → `azurerm_role_assignment`
5. **Map IAM policies to RBAC:** AWS managed policies → Azure built-in roles
6. **Attach to VM:** Add `identity { type = "UserAssigned", identity_ids = [...] }` block to VM

## Common IAM Policy to Azure RBAC Mapping
| AWS Policy | Azure RBAC Role |
|-----------|----------------|
| AmazonS3ReadOnlyAccess | Storage Blob Data Reader |
| AmazonS3FullAccess | Storage Blob Data Contributor |
| AmazonEC2ReadOnlyAccess | Reader (scoped to RG) |
| AmazonVPCReadOnlyAccess | Network Contributor |
| AdministratorAccess | Contributor (NOT Owner — least privilege!) |

## Variables to Extract
- `identity_name`
- `role_assignments` (map of scope → role)

## Validation Criteria
- No `aws_iam_*` references remain
- No instance profiles
- Role assignments use least-privilege RBAC roles
- Identity is attached to target resource

## Related
- [[azurerm_user_assigned_identity]]
