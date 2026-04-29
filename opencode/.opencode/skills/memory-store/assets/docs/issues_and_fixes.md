## AWS → Azure Terraform Migration Learnings

### Issue 1: Terraform Azure Provider Syntax
**Description:** Terraform validation failures due to Azure provider-specific syntax differences from AWS

**Fix:**
- Changed `idle_timeout` to `request_timeout` (Azure Load Balancer uses request_timeout)
- Corrected route configuration syntax for Azure Virtual Network
- Ensured proper tag formatting per Azure conventions

**Steps:**
1. Review Azure Terraform provider documentation for exact property names
2. Validate each resource type against Azure provider schema
3. Test with `terraform validate` and `terraform plan`

**Tags:** terraform, azure, syntax, validation

---

### Issue 2: Code Review Iterations
**Description:** Required 3 developer retries to pass code review

**Fix:** Developer addressed each round of review comments until approval

**Steps:**
1. First iteration: Fixed resource naming conventions
2. Second iteration: Corrected provider block configuration
3. Third iteration: Added required tags and metadata

**Tags:** code-review, iterations, approval

---

### Issue 3: Incomplete Migration Coverage
**Description:** 75% resource coverage achieved, missing environment configurations

**Fix:** Documented gap for future migrations to include environment-specific configs

**Steps:**
1. Map all environment variables from source
2. Include environment-specific.tf files in migration scope
3. Validate complete coverage before final approval

**Tags:** coverage, environment-configs, incomplete

---

## Resource Mappings Learned
| AWS | Azure |
|-----|-------|
| VPC | Virtual Network |
| EC2 | Azure VM |
| ELB | Load Balancer |
| S3 | Blob Storage |
| RDS | Azure SQL / Cosmos DB |
| IAM | Azure AD / Managed Identity |
| CloudWatch | Azure Monitor |
| Route53 | Azure DNS |