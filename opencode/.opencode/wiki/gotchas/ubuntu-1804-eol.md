---
id: ubuntu-1804-eol
severity: critical
discovered_in_run: 1
last_updated: "2026-04-19"
---
# Ubuntu 18.04 is End of Life

## Problem
AWS source code uses AMI lookup maps that resolve to Ubuntu images. During migration, agents may hardcode `"18.04-LTS"` in `source_image_reference.sku`. Ubuntu 18.04 reached End of Life and receives no security updates.

## Fix
Use `22.04-LTS` or `24.04-LTS`:
```hcl
variable "vm_image_sku" {
  type        = string
  description = "Ubuntu image SKU for VMs"
  default     = "22_04-lts-gen2"
  validation {
    condition     = !contains(["18.04-LTS", "16.04-LTS"], var.vm_image_sku)
    error_message = "Cannot use EOL Ubuntu versions."
  }
}
```

## Related
- [[azurerm_linux_virtual_machine]]
