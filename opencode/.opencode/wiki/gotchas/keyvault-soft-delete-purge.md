# Gotcha: Key Vault soft-delete & purge protection reserve the name

Azure Key Vault has **soft-delete always enabled** (cannot be turned off), and
`purge_protection_enabled = true` is recommended for production. Consequences:

- A deleted vault is **retained (soft-deleted) for `soft_delete_retention_days`
  (7–90)** and its **name stays reserved** during that window — re-creating a
  vault with the same name fails with `VaultAlreadyExists` / conflict until it is
  purged (and purge is **blocked** when purge protection is on).
- `terraform destroy` then re-`apply` of the same vault name will fail mid-window.

## Fix / guidance
- Treat Key Vaults as **stateful/long-lived**; generate an `imports.tf` `import {}`
  block rather than destroy+recreate.
- For ephemeral dev/test, either use unique per-run names or set
  `purge_protection_enabled = false` (dev only) with a short retention.
- Prefer `enable_rbac_authorization = true` (RBAC) over legacy access policies.
- Same "name reserved after delete" behavior affects API Management and a few
  other services — don't assume destroy frees the name immediately.
