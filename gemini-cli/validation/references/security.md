# Target Cloud Security Standards (DevSecOps)

This document defines the baseline security policies and compliance rules for migrated cloud resources.

## 1. Secrets and Credential Management
*   **Zero Hardcoded Credentials**: No passwords, database connection strings, keys, or API tokens may be checked into IaC configurations or application repositories.
*   **Azure Key Vault Enforcement**:
    *   All secrets must be stored in Azure Key Vault.
    *   Key Vaults must have `purge_protection_enabled = true` and `soft_delete_retention_days = 90`.
    *   Key Vault Access Policies must use Azure RBAC (Role-Based Access Control) instead of legacy vault access policies.
*   **Managed Identities**: Applications must access Azure resources (databases, storage accounts, etc.) using System-Assigned or User-Assigned Managed Identities. Service principals with password credentials should be avoided.

## 2. Infrastructure & Network Security
*   **TLS Requirements**: All public-facing endpoints (App Services, Load Balancers, API Management) must enforce a minimum TLS version of `1.2`.
*   **NSG Rule Restrictions**:
    *   Inbound security rules must not contain wildcard source address scopes (`*` or `0.0.0.0/0`) for administrative ports (e.g., SSH `22`, RDP `3389`).
    *   Inbound SSH/RDP must be restricted to internal corporate IP address blocks.
*   **Storage Access Control**:
    *   Storage accounts must have `public_network_access_enabled = false` unless explicitly authorized.
    *   `allow_nested_items_to_be_public = false` must be enforced on all blob containers.
    *   Shared Access Signature (SAS) tokens must have a maximum validity period of 2 hours.

## 3. Container & Kubernetes Security
*   **Vulnerability Scanning**: All container images must undergo vulnerability scanning before being pushed to Azure Container Registry (ACR).
*   **AKS Access Control**: AKS clusters must have Azure AD integration enabled, with Kubernetes local accounts disabled.
