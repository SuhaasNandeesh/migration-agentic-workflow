---
resource: azurerm_linux_virtual_machine
provider: azurerm
aws_equivalent: aws_instance
last_updated: "2026-04-19"
source_runs: 1
---
# azurerm_linux_virtual_machine

## Overview
Azure Linux Virtual Machine resource. Replaces AWS EC2 `aws_instance`.

## Key Differences from AWS EC2

| Aspect | AWS (`aws_instance`) | Azure (`azurerm_linux_virtual_machine`) |
|--------|---------------------|----------------------------------------|
| Image lookup | `ami` ID or data source lookup | `source_image_reference` block (publisher/offer/sku/version) |
| Instance sizing | `instance_type` (e.g., `t2.micro`) | `size` (e.g., `Standard_B1s`) |
| Network attachment | `subnet_id` directly on instance | Separate `azurerm_network_interface` resource required |
| Public IP | `associate_public_ip_address = true` | Separate `azurerm_public_ip` + NIC IP config |
| IAM/Identity | `iam_instance_profile` | `identity` block with `UserAssigned` type |
| User data | `user_data` attribute (base64) | `azurerm_virtual_machine_extension` with CustomScript |
| SSH key | `key_name` referencing `aws_key_pair` | `admin_ssh_key` block inline |
| Storage | `root_block_device` block | `os_disk` block |

## Required Variables (always extract, never hardcode)
- `vm_size` — VM SKU (validate with `^Standard_` regex)
- `admin_username` — SSH admin user (never hardcode `"azureuser"`)
- `vm_image_sku` — OS image SKU (never use EOL versions like `18.04-LTS`)
- `os_disk_type` — Storage type (`Premium_LRS`, `Standard_LRS`, `StandardSSD_LRS`)
- `ssh_public_key` — Path or value of SSH public key

## Gotchas
- [[ubuntu-1804-eol]] — Ubuntu 18.04 is End of Life, use `22.04-LTS` or `24.04-LTS`
- [[dynamic-vs-static-public-ip]] — If using Standard LB, public IP must be `Static` + `Standard` SKU
- NIC must be created BEFORE the VM — use `depends_on` or reference
- `os_disk.disk_encryption_set_id` should be set for encryption at rest
- Always add `lifecycle { prevent_destroy = true }` for production VMs

## Tags (mandatory)
```hcl
tags = {
  environment = var.environment
  project     = var.project_name
  managed_by  = "terraform"
  cost_center = var.cost_center
}
```

## Related
- [[aws-ec2-to-azure-vm]] — Full migration pattern
- [[azurerm_network_interface]] — Required companion resource
- [[azurerm_public_ip]] — For public-facing VMs
