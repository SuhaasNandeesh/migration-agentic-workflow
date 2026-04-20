# Azure Storage Backend Configuration
# Auto-migrated from source platform by Migration Factory

terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "stterraformstate"
    container_name       = "tfstate"
    key                  = "migration/terraform.tfstate"
    use_oidc             = true
  }
}
