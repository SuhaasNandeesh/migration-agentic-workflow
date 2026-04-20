# STANDARD TERRAFORM MODULE TEMPLATE

variable "resource_name" {
  type = string
}

resource "example_compute" "main" {
  name = var.resource_name
}

# REQUIRED:
# - must pass fmt
# - must pass validate
# - must pass plan