---
resource: github_actions_workflow
kind: Workflow
last_updated: "2026-04-22"
source_runs: 0
---
# GitHub Actions Workflow

## Overview
CI/CD pipeline definition for GitHub Actions. Target format for pipeline migrations from GitLab CI and Jenkins.

## Required Structure
```yaml
name: <descriptive name>

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

permissions:
  contents: read    # Least privilege

jobs:
  <job-name>:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: <step description>
        run: <command>
```

## Best Practices
- Always pin action versions with SHA (`uses: actions/checkout@<sha>`) or at minimum with major version (`@v4`)
- Always set `permissions:` block (deny by default)
- Use `environment:` for deployment jobs (enables approval gates)
- Use `concurrency:` to prevent duplicate runs
- Cache dependencies with `actions/cache@v4`
- Use `actions/setup-*` for language toolchains
- Store secrets in GitHub Secrets, NEVER hardcode
- Use reusable workflows for shared logic across repos

## Security Rules
- `permissions: contents: read` by default — grant more only as needed
- NEVER use `permissions: write-all`
- Pin all third-party actions to SHA
- Use `GITHUB_TOKEN` instead of PATs where possible
- Use OIDC (`id-token: write`) for cloud auth instead of stored credentials

## Gotchas
- GitHub Actions has a 6-hour job timeout (can be lowered with `timeout-minutes:`)
- Matrix builds can hit rate limits on large repos
- Self-hosted runners need manual security hardening
- Artifact retention is 90 days by default
- Secrets are not available in forked PR workflows (security)

## Related
- [[gitlab-ci-to-github-actions]]
- [[jenkins-to-github-actions]]
