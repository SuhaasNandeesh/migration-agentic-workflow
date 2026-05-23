# Migration Completeness Standard

PURPOSE:
Ensures every migration run produces a complete, verified, deployment-ready output.

RESOURCE COVERAGE:
- Every source resource must have a corresponding target resource OR be explicitly flagged as "deferred/not applicable"
- No source resource may be silently dropped
- Coverage percentage must be reported by the evaluator
- Target: 100% coverage for direct + functional mappings

SOURCE PLATFORM CLEANUP (MANDATORY):
- No source platform provider references in output code
- No source platform resource type prefixes (aws_*, google_*, etc.)
- No source platform endpoints, ARNs, account IDs, or project IDs
- No source platform CLI commands in scripts
- No source platform SDK imports in application code
- No source platform container registry references in image fields
- No source platform identity annotations in Kubernetes manifests
- No source platform-specific environment variables

TARGET PLATFORM CORRECTNESS:
- All target resources use correct API versions
- All target resources follow platform naming conventions
- All target resources include required tags/labels
- All target resources use platform-recommended modules/patterns where available

FUNCTIONAL EQUIVALENCE:
- Migrated resource must serve the same purpose as the source
- Compute sizes/tiers must be comparable (not necessarily identical)
- Network rules must preserve the same access patterns
- Identity/auth must provide equivalent permissions
- Storage must preserve capacity and performance characteristics

DOCUMENTATION:
- Every service/module must have a migration note explaining what changed
- Architecture Decision Records required for non-obvious mappings
- Deployment runbook must exist with step-by-step instructions
- Rollback procedure must be documented

FAIL IF:
- Any source resource has no corresponding target or explicit deferral
- Source platform references detected in output
- Missing migration documentation
- Functional equivalence not verified
