---
name: azure-naming-validator
description: "Deterministic offline validator for Azure resource naming rules (length, allowed characters, global uniqueness). Catches a common class of migration errors that `terraform validate` misses and that otherwise only fail at apply time — no cloud credentials required."
---
# Azure Naming & Constraints Validator Skill

Azure enforces strict, **per-resource-type** naming rules. `terraform validate`
does NOT check them — an over-length or wrong-charset name only fails when you
`apply` against the live Azure API. This skill validates generated `azurerm_*`
resource names **offline and deterministically**, so naming bugs are caught in
the gate loop instead of in production.

## Usage

```bash
# Scan generated Terraform and write a JSON report (exit code 1 if any error):
python3 .agents/skills/azure-naming-validator/run.py \
  --dir output/target \
  --output output/artifacts/azure-naming-results.json

# Quick single-name check:
python3 .agents/skills/azure-naming-validator/run.py \
  --check azurerm_storage_account --name "myprodstorage01"
```

- **Literal names** are fully validated (length + charset).
- **Interpolated names** (e.g. `"st${var.env}"`) can't be resolved offline, so
  the static prefix is checked and a `warning` reminds you to verify the resolved
  value (especially for globally-unique resources).
- Exit code `0` = no errors, `1` = at least one error-severity violation (gate-friendly).

## Constraints Reference (use this when generating names, not just validating)

| Resource | Length | Allowed characters | Global? |
|---|---|---|---|
| `azurerm_storage_account` | 3–24 | lowercase letters + digits only | ✅ |
| `azurerm_key_vault` | 3–24 | alphanumerics + hyphens, start with letter, no `--` | ✅ |
| `azurerm_container_registry` | 5–50 | alphanumerics only | ✅ |
| `azurerm_cosmosdb_account` | 3–44 | lowercase letters, digits, hyphens | ✅ |
| `azurerm_postgresql_flexible_server` / `_mysql_` | 3–63 | lowercase letters, digits, hyphens | ✅ |
| `azurerm_redis_cache` | 1–63 | alphanumerics + hyphens (no `--`) | ✅ |
| `azurerm_servicebus_namespace` / `eventhub_namespace` | 6–50 | alphanumerics + hyphens, start with letter | ✅ |
| `azurerm_linux_function_app` / web app / windows variants | 2–60 | alphanumerics + hyphens (part of `*.azurewebsites.net`) | ✅ |
| `azurerm_resource_group` | 1–90 | alphanumerics, `_ . ( ) -` (no trailing `.`) | ❌ |
| `azurerm_virtual_network` | 2–64 | alphanumerics, `_ . -` | ❌ |
| `azurerm_subnet` / `network_security_group` / `public_ip` / `nat_gateway` / `lb` | 1–80 | alphanumerics, `_ . -` | ❌ |
| `azurerm_kubernetes_cluster` | 1–63 | alphanumerics, `_ -` | ❌ |
| `azurerm_windows_virtual_machine` | ≤15 | alphanumerics + hyphen (Windows computer-name limit) | ❌ |
| `azurerm_linux_virtual_machine` | 1–64 | alphanumerics, `_ . -` | ❌ |

> **Globally-unique** names (storage accounts, key vaults, ACR, Cosmos DB, App
> Service, Service Bus, flexible servers) must be unique across **all** of Azure
> — always include an org/env/region discriminator (e.g. `st<app><env><region>`).
