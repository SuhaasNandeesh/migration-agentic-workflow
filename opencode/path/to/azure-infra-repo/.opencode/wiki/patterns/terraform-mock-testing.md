# Offline Mock Validation using .tftest.hcl Test Suites

Terraform 1.6+ introduced a native test framework (`terraform test`) which enables writing test suites in HCL. This provides robust offline verification (dry-run planning) to validate variables, inputs, complex validation blocks, naming conventions, and resource tag compliance before attempting execution in active environments.

---

## 1. Golden Pattern: `.tftest.hcl` Specification

Create a dedicated `tests/` directory or write test definition files with the `.tftest.hcl` extension in each environment workspace.

```hcl
# --- tests/validation.tftest.hcl ---

# Set default variables for the test run
variables {
  environment_name      = "dev"
  vm_size               = "Standard_B2s"
  system_node_count     = 1
  storage_redundancy    = "LRS"
}

# Run step 1: Validate variable constraints during planning
run "validate_dev_rules" {
  command = plan

  # Assert environment-specific compute rules
  assert {
    condition     = can(regex("^Standard_B", var.vm_size))
    error_message = "Dev/Test environments must use burstable Standard B-series compute resources."
  }

  assert {
    condition     = var.system_node_count <= 2
    error_message = "Dev/Test environments must not exceed 2 active system nodes."
  }
}

# Run step 2: Validate mandatory FinOps tagging structures
run "validate_tags" {
  command = plan

  assert {
    condition     = length(keys(azurerm_resource_group.rg.tags)) >= 4
    error_message = "Resources must contain at least 4 mandatory FinOps tags."
  }

  assert {
    condition     = lookup(azurerm_resource_group.rg.tags, "CostCenter", "") == "CC-999-DEVOPS"
    error_message = "Default DevOps CostCenter tag 'CC-999-DEVOPS' must be applied."
  }
}
```

---

## 2. Benefits of Offline Test Suites

- **No Active Cloud Credentials Required**: By executing tests with `command = plan`, Terraform evaluates validation expressions and configuration outputs statically without requiring active subscriptions or API authentication.
- **Strict Boundary Checkers**: Tests allow validation of intricate multi-conditional expressions that cannot be easily caught by basic schema linters.
- **Fail-Fast in QA Gates**: The QA Tester agent runs `terraform test` in the workspace, immediately catching floating provider violations, incorrect tags, and oversized VMs.

---

## 3. Execution Commands in CI Pipelines

To run test suites as a pre-deploy validation gate:

```bash
# Initialize target environment
terraform init -backend=false

# Run all test files (.tftest.hcl) offline
terraform test
```
