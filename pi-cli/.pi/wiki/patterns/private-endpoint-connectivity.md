# Golden Pattern: Private Endpoint Connectivity

To prevent data exfiltration and satisfy enterprise security rules, sensitive backend services (including **Azure Key Vault**, **Azure SQL Database**, and **Azure Storage Accounts**) must be configured behind **Private Endpoints** with public network ingress disabled.

---

## 1. Terraform Infrastructure Configuration

This blueprint provisions a Private Endpoint for an Azure Key Vault and establishes the required Private DNS Zone mapping within the host VNet.

```hcl
# 1. Create Private DNS Zone for Key Vault
resource "azurerm_private_dns_zone" "vault_dns" {
  name                = "privatelink.vaultcore.azure.net"
  resource_group_name = var.resource_group_name
}

# 2. Link DNS Zone to Hub/Spoke VNet
resource "azurerm_private_dns_zone_virtual_network_link" "dns_vnet_link" {
  name                  = "vnet-link-vault-dns"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.vault_dns.name
  virtual_network_id    = var.vnet_id
}

# 3. Create Private Endpoint for Key Vault
resource "azurerm_private_endpoint" "kv_private_endpoint" {
  name                = "pe-keyvault-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.private_endpoint_subnet_id

  private_service_connection {
    name                           = "psc-keyvault-${var.environment}"
    private_connection_resource_id = var.key_vault_id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "dns-group-vault"
    private_dns_zone_ids = [azurerm_private_dns_zone.vault_dns.id]
  }
}
```

---

## 2. Restricting Public Access

To enforce the private-only policy, you must explicitly disable public network access on the target resources.

```hcl
resource "azurerm_key_vault" "kv" {
  name                        = "kv-secure-${var.environment}"
  location                    = var.location
  resource_group_name         = var.resource_group_name
  tenant_id                   = var.tenant_id
  sku_name                    = "standard"
  
  # STRICT ENFORCEMENT: Block all public ingress
  public_network_access_enabled = false

  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny" # Reject all traffic not arriving via private endpoints
  }
}
```

---

## 3. Production Rules & Gotchas

* **Subnet Security Rules:** Ensure that the subnet holding your Private Endpoints has `private_endpoint_network_policies_enabled` set to `true` (or `false` on older provider versions depending on your policy enforcement needs). This allows Network Security Groups (NSGs) to be applied to Private Endpoint traffic.
* **DNS Resolution Chain:** Any client attempting to resolve the Key Vault's FQDN (e.g. `kv-secure.vault.azure.net`) from inside the VNet must resolve it to the private IP (e.g. `10.0.2.5`) via the linked Private DNS Zone. External public DNS queries will resolve to the public endpoint but will be denied by the firewall.
* **Transit Routing (Validation Runners):** To run Terraform plan validation pipelines against a private Key Vault, the GitHub Actions runner (or build machine) must reside in a subnet that has direct network transit (or VNet Peering) to the `private_endpoint_subnet_id`.
