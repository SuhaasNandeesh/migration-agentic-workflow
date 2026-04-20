---
pattern: aws-ec2-to-azure-vm
complexity: functional
last_updated: "2026-04-19"
source_runs: 1
---
# AWS EC2 to Azure Linux VM

## Migration Steps

1. **Replace resource type:** `aws_instance` → `azurerm_linux_virtual_machine`
2. **Create NIC:** Azure VMs need a separate `azurerm_network_interface` (AWS attaches directly)
3. **Create Public IP:** If needed, create `azurerm_public_ip` (AWS uses `associate_public_ip_address`)
4. **Map instance type:** `t2.micro` → `Standard_B1s`, `t3.medium` → `Standard_B2s`, etc.
5. **Map AMI to image reference:** Replace AMI ID with `source_image_reference { publisher, offer, sku, version }`
6. **Map key pair:** Move from `key_name` → inline `admin_ssh_key` block
7. **Map IAM:** `iam_instance_profile` → `identity { type = "UserAssigned" }`
8. **Map storage:** `root_block_device` → `os_disk` block
9. **Map user data:** `user_data` → `azurerm_virtual_machine_extension` with CustomScript
10. **Add tags:** Comprehensive tag block with environment, project, managed_by

## Variables to Extract
- `vm_size` (from hardcoded instance_type)
- `admin_username` (never hardcode "azureuser")
- `vm_image_sku` (from AMI, use 22.04-LTS not 18.04)
- `os_disk_type` (Premium_LRS for prod, Standard_LRS for dev)
- `ssh_public_key` (from key_name reference)

## Validation Criteria
- No `aws_instance` references remain
- No hardcoded AMI IDs
- NIC resource exists and is linked
- Tags applied to all resources
- SSH key is parameterized, not hardcoded

## Related
- [[azurerm_linux_virtual_machine]]
- [[azurerm_network_interface]]
- [[ubuntu-1804-eol]]
