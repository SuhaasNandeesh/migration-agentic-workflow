# Target Cloud Architecture Standards (Azure)

This document defines the mandatory architecture standards for resources migrated to Azure. These standards must be programmatically checked and enforced across all generated IaC (Terraform/Bicep) definitions.

## 1. Resource Naming Conventions
All resources must follow a standardized naming structure:
`[resource-prefix]-[environment]-[application-name]-[region]-[index]`

### Standard Prefixes:
*   Resource Group: `rg-`
*   Virtual Network: `vnet-`
*   Subnet: `snet-`
*   Network Security Group: `nsg-`
*   Linux Virtual Machine: `vm-`
*   Storage Account: `st` (Lowercase, alphanumeric only, max 24 chars)
*   Key Vault: `kv-`

## 2. Compute Series Selection
To optimize costs, workloads must align with the following compute families:
*   **Dev/Test Environments**: Must utilize burstable compute series (`Standard_B2s` or `Standard_D2s_v5`).
*   **Production Environments**: Must utilize general purpose or compute-optimized series (`Standard_D4s_v5` or `Standard_F4s_v2`).
*   Virtual machines must have managed disks enabled and use `Premium_LRS` or `StandardSSD_LRS` storage types.

## 3. Network Architecture & Segmentation
*   All virtual networks (`vnet`) must declare address spaces within RFC 1918 private scopes.
*   **Subnet Boundaries**:
    *   Web/Public Subnets: `/24` or `/26` prefixes.
    *   Application Subnets: `/24` prefix.
    *   Database/Private Subnets: `/28` or `/27` prefixes.
*   Every subnet must be associated with a dedicated Network Security Group (NSG).
*   Direct public IP attachments to backend virtual machines are strictly prohibited. Traffic must route through an Azure Application Gateway or Azure Bastion host.
