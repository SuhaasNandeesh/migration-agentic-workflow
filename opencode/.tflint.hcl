# tflint configuration for the migration workspace (Azure target).
#
# Enables the azurerm ruleset so tflint catches Azure-specific issues (invalid
# SKUs, deprecated arguments, naming-rule violations) on top of the generic
# Terraform checks. Activate the plugin once with `tflint --init` (this pulls the
# plugin binary from GitHub and requires network on first run; it is then cached
# in ~/.tflint.d/ and works offline thereafter). Agents run `tflint --init`
# opportunistically and degrade gracefully if the plugin cannot be fetched.
#
# Agents point tflint at this file via: export TFLINT_CONFIG_FILE="$(pwd)/.tflint.hcl"

plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

plugin "azurerm" {
  enabled = true
  version = "0.27.0"
  source  = "github.com/terraform-linters/tflint-ruleset-azurerm"
}
