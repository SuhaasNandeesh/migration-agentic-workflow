# Target Platform Standard (Azure Example — Configurable)

> This standard contains target-platform-specific rules. Update this file when migrating to a different target platform.

CURRENT TARGET: Azure

NAMING CONVENTIONS:
- Resource Group: `rg-<project>-<env>-<region>`
- AKS Cluster: `aks-<project>-<env>-<region>`
- Key Vault: `kv-<project>-<env>` (max 24 chars)
- Storage Account: `st<project><env>` (lowercase, no hyphens, max 24 chars)
- Container Registry: `cr<project><env>` (lowercase, no hyphens)
- Virtual Network: `vnet-<project>-<env>-<region>`
- Subnet: `snet-<purpose>-<env>`
- NSG: `nsg-<purpose>-<env>`
- Public IP: `pip-<purpose>-<env>`
- Load Balancer: `lb-<purpose>-<env>`
- Application Gateway: `agw-<purpose>-<env>`
- Managed Identity: `id-<purpose>-<env>`
- PostgreSQL: `psql-<project>-<env>`

REQUIRED TAGS (on all resources):
- `environment` — dev, staging, production
- `project` — project name
- `managed-by` — "terraform" or tool used
- `cost-center` — billing allocation
- `owner` — team or individual
- `created-by` — "migration-factory" (for auto-generated resources)

PROVIDER:
- Use latest stable azurerm provider version
- Features block must be declared (even if empty)
- Backend must use Azure Storage Account with encryption

IDENTITY:
- Use Managed Identity (User-Assigned) for all service authentication
- Use Workload Identity for Kubernetes workloads
- Avoid Service Principal secrets — use federated credentials

REGIONAL STRATEGY:
- Primary and paired region for disaster recovery
- Region specified via variable, never hardcoded

MODULES:
- Prefer Azure Verified Modules (AVM) where available
- Custom modules for patterns not covered by AVM

> **To adapt for a different target platform:**
> Replace the naming conventions, tags, provider requirements, and identity section
> with the equivalent rules for your target platform (GCP, OCI, etc.)

FAIL IF:
- Naming convention not followed
- Missing required tags
- Hardcoded region
- Service Principal secrets used instead of Managed Identity
