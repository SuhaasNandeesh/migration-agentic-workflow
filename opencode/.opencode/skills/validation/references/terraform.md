REQUIRED VALIDATION:
- terraform fmt must pass
- terraform validate must pass
- terraform plan must succeed (if provider credentials available)

PROVIDER REQUIREMENTS:
- Target platform provider must be declared with required feature blocks
- Backend must use target platform storage (not source platform)
- Provider version must be pinned (not "latest")
- Required provider versions must be declared in terraform block

BEST PRACTICES:
- Use variables for all environment-specific values
- Modular design — one module per logical resource group
- No hardcoded values (regions, names, sizes, IPs)
- Use data sources to reference existing resources
- Use locals for computed values
- Output all resource IDs and endpoints needed by other modules

NAMING:
- Follow target platform naming conventions
- Use consistent prefix/suffix patterns
- Resources must have required tags/labels per target platform standards

MIGRATION-SPECIFIC:
- No source platform provider references in output (no residual aws/google/etc.)
- No source platform resource types in output
- No source platform endpoints, ARNs, or identifiers
- Auto-generated comment at top indicating migration origin

STATE:
- State backend must use target platform storage with encryption
- State locking must be enabled
- Separate state per environment

FAIL IF:
- terraform fmt fails
- terraform validate fails
- Source platform references found in output
- Missing required tags/labels