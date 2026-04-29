REQUIRED STAGES:
1. build
2. test (unit + integration)
3. security (SAST, dependency scan, container scan, secret scan)
4. deploy (with environment protection for production)
5. artifact (build outputs, test reports)

FORMAT:
- Must be valid YAML for the target CI/CD platform
- Must pass platform-specific linting (actionlint for GitHub Actions, etc.)

AUTHENTICATION:
- Use OIDC / federated credentials for cloud authentication (MANDATORY)
- No static cloud credentials stored as secrets
- Token permissions must be minimal (principle of least privilege)

VERSIONING:
- All third-party plugins/actions/tasks pinned to specific version or SHA
- No "@latest" or unversioned references

ENVIRONMENTS:
- Separate pipeline definitions or stages per environment (dev, staging, prod)
- Production deployments must require environment protection/approval
- Concurrency controls to prevent parallel prod deployments

REUSABILITY:
- Common patterns should use the platform's reusable mechanism
  (GitHub: reusable workflows, GitLab: includes, Jenkins: shared libraries)
- DRY — avoid duplicating pipeline logic across services

MIGRATION-SPECIFIC:
- No source CI/CD platform syntax in output
- All pipeline variables translated to target format
- All plugin/task/action references are target platform equivalents
- Runner/agent configs use target platform runners

FAIL IF:
- Required stage is missing
- Static cloud credentials used
- Actions/plugins not pinned to version
- Source CI/CD platform syntax detected
- YAML syntax invalid