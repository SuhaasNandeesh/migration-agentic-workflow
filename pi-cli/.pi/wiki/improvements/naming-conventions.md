---
id: naming-conventions
last_updated: "2026-04-22"
used_by: [developer, validator]
---
# Naming Conventions & Folder Structure

This document defines the MANDATORY naming conventions for all generated files.
Developer MUST follow these; Validator MUST enforce them.

## Terraform File Naming

| File Name | Purpose |
|-----------|---------|
| `main.tf` | Primary resource definitions |
| `variables.tf` | Input variable declarations |
| `outputs.tf` | Output value declarations |
| `providers.tf` | Provider configuration + required_providers |
| `backend.tf` | State backend configuration (environments only) |
| `locals.tf` | Local value calculations |
| `data.tf` | Data source lookups |
| `versions.tf` | Terraform version constraints (if separate from providers) |

## Folder Structure

```
output/<target>_Modules-<Platform>/
├── README.md                          ← Project-level documentation
├── environments/
│   ├── development/
│   │   ├── main.tf                    ← Root module calling child modules
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── providers.tf
│   │   ├── backend.tf
│   │   └── terraform.tfvars           ← Environment-specific values
│   ├── staging/
│   │   └── ... (same structure)
│   └── production/
│       └── ... (same structure)
├── modules/
│   ├── resource_group/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md                  ← Module documentation
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── compute/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── security/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── <category>/
│       └── ... (same pattern)
└── .github/
    └── workflows/
        └── terraform.yml              ← CI/CD pipeline (if migrated)
```

## Resource Naming Pattern

All Azure resources MUST follow this naming convention:
```
<type>-<project>-<environment>-<region>
```

| Resource Type | Prefix | Example |
|---------------|--------|---------|
| Resource Group | `rg` | `rg-myproject-dev-eastus` |
| Virtual Network | `vnet` | `vnet-myproject-dev-eastus` |
| Subnet | `snet` | `snet-myproject-app-dev-eastus` |
| Network Security Group | `nsg` | `nsg-myproject-app-dev-eastus` |
| Public IP | `pip` | `pip-myproject-lb-dev-eastus` |
| Load Balancer | `lb` | `lb-myproject-dev-eastus` |
| Virtual Machine | `vm` | `vm-myproject-web-dev-eastus` |
| Network Interface | `nic` | `nic-myproject-web-dev-eastus` |
| NAT Gateway | `ng` | `ng-myproject-dev-eastus` |
| Key Vault | `kv` | `kv-myproject-dev-eastus` |
| Storage Account | `st` | `stmyprojectdeveastus` (no hyphens — Azure limitation) |
| Managed Identity | `id` | `id-myproject-dev-eastus` |

### Implementation
```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}-${var.location}"
}

resource "azurerm_virtual_network" "main" {
  name = "vnet-${local.name_prefix}"
  # ...
}
```

## Variable Naming

| Pattern | Example | Rule |
|---------|---------|------|
| `var.<resource>_<attribute>` | `var.vm_size` | Resource-specific settings |
| `var.environment` | `"development"` | Always required |
| `var.project_name` | `"myproject"` | Always required |
| `var.location` | `"eastus"` | Always required |
| `var.tags` | `map(string)` | Always required |

## Output Naming

Outputs follow: `<resource>_<attribute>`
```hcl
output "vnet_id" { value = azurerm_virtual_network.main.id }
output "vnet_name" { value = azurerm_virtual_network.main.name }
output "subnet_ids" { value = { for k, v in azurerm_subnet.main : k => v.id } }
```
