# GitHub Actions Standard

PURPOSE:
Ensures all GitHub Actions workflows follow best practices for security, reliability, and maintainability.

STRUCTURE:
- Must have `name:` (descriptive workflow name)
- Must have `on:` with explicit trigger events
- Must have `permissions:` block limiting GITHUB_TOKEN scope
- Must have descriptive job names

SECURITY:
- Use OIDC for cloud authentication (`azure/login`, `google-github-actions/auth`, `aws-actions/configure-aws-credentials`)
- Never store cloud credentials as repository secrets
- Pin ALL action references to full commit SHA (not tags, not @latest)
  Example: `actions/checkout@a5ac7e51b41094c92402da3b24376905380afc29` (v4)
- Add `permissions:` block and use principle of least privilege
- Use GitHub Environments with protection rules for production

REUSABILITY:
- Common pipeline logic should use reusable workflows (`workflow_call`)
- Repeated step sequences should be composite actions
- Organization-wide patterns in `.github` repository

TRIGGERS:
- PR workflows: `pull_request` (not `pull_request_target` unless needed)
- Deploy workflows: `push` to main/release branches or `workflow_dispatch`
- Scheduled workflows: `schedule` with cron

CONCURRENCY:
- Production deploy workflows must have `concurrency:` to prevent parallel runs
- Use `cancel-in-progress: true` for PR workflows

ARTIFACTS:
- Build outputs → `actions/upload-artifact@v4`
- Cross-job data → `actions/upload-artifact` + `actions/download-artifact`
- Caching → `actions/cache@v4` with proper key patterns

ERROR HANDLING:
- Critical steps must have `continue-on-error: false` (default)
- Notification steps should have `if: failure()`
- Cleanup steps should have `if: always()`

FAIL IF:
- Missing `permissions:` block
- Actions referenced by tag instead of SHA
- Static cloud credentials used
- Missing security scanning steps
- YAML syntax invalid (actionlint)
