# Gotcha: Storage Account name = 3–24 lowercase alphanumerics, globally unique

`azurerm_storage_account.name` is the strictest common Azure naming rule and a
frequent apply-time failure:

- **3–24 characters**, **lowercase letters and digits ONLY**. No hyphens, no
  underscores, no uppercase. (`my-prod-storage` and `MyStorage` are both INVALID.)
- **Globally unique** across all of Azure (it becomes `<name>.blob.core.windows.net`).

## Fix
- Use a compact discriminated pattern: `st<app><env><region?>` → e.g. `stshopprodeus`.
- Strip hyphens/underscores when deriving from an S3 bucket name.
- Always include an org/env discriminator so the global-uniqueness constraint is met.
- Validate offline before apply:
  `python3 .opencode/skills/azure-naming-validator/run.py --dir . --output output/artifacts/azure-naming-results.json`

Container/blob names CAN have hyphens — only the **account** name is restricted.
The same "globally unique, restricted charset" class also applies to Key Vault,
ACR, Cosmos DB, App Service, Service Bus, and flexible servers.
