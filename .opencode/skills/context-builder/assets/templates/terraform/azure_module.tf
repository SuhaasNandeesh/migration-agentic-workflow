# Auto-migrated from source platform by Migration Factory
# Target Platform: Azure (azurerm provider)

terraform {
  required_version = ">= 1.11.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# --- Variables ---
variable "project_name" {
  type        = string
  description = "Project name used in resource naming"
}

variable "environment" {
  type        = string
  description = "Environment (dev, staging, production)"
}

variable "location" {
  type        = string
  description = "Azure region for resources"
  default     = "eastus2"
}

variable "tags" {
  type        = map(string)
  description = "Common tags applied to all resources"
  default     = {}
}

locals {
  common_tags = merge(var.tags, {
    environment = var.environment
    project     = var.project_name
    managed-by  = "terraform"
    created-by  = "migration-factory"
  })
}

# --- Resource Group ---
resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project_name}-${var.environment}-${var.location}"
  location = var.location
  tags     = local.common_tags
}

# --- Module Resources Below ---
# Replace this section with migrated resources
