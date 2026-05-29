# AWS Route 53 → Azure DNS

| Source (AWS) | Target (Azure) |
|---|---|
| `aws_route53_zone` (public) | `azurerm_dns_zone` |
| `aws_route53_zone` (private) | `azurerm_private_dns_zone` (+ `azurerm_private_dns_zone_virtual_network_link`) |
| `aws_route53_record` | `azurerm_dns_a_record` / `_cname_record` / `_txt_record` / etc. |
| `aws_route53_record` (alias to ELB) | `azurerm_dns_a_record` with `target_resource_id` (alias) |
| weighted/latency routing | Azure Traffic Manager (`azurerm_traffic_manager_profile`) |

## Golden Example
```hcl
resource "azurerm_dns_zone" "main" {
  name                = var.dns_zone_name        # e.g. "example.com"
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

resource "azurerm_dns_a_record" "app" {
  name                = "app"
  zone_name           = azurerm_dns_zone.main.name
  resource_group_name = azurerm_resource_group.main.name
  ttl                 = 300
  records             = [azurerm_public_ip.app.ip_address]
}
```

## Gotchas
- **Per-record-type resources** — Azure has a distinct resource per record type (`azurerm_dns_a_record`, `_cname_record`, ...), unlike Route 53's single `aws_route53_record` with a `type` argument. Split accordingly.
- **Delegation/NS change happens at the registrar** — Terraform creates the zone but the domain's nameservers must be repointed to Azure's NS set (`azurerm_dns_zone.main.name_servers`) out of band.
- Private hosted zones require explicit **VNet links**; there's no automatic association.
- Route 53 health-check/failover routing → **Traffic Manager** or **Front Door**, not Azure DNS.
