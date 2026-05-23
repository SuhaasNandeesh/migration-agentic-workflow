---
pattern: gitlab-ci-to-github-actions
complexity: functional
last_updated: "2026-04-22"
source_runs: 0
---
# GitLab CI to GitHub Actions

## Migration Steps

1. **Replace file:** `.gitlab-ci.yml` → `.github/workflows/<pipeline-name>.yml`
2. **Map stages to jobs:** GitLab `stages:` → GitHub Actions `jobs:` with `needs:` for ordering
3. **Map variables:** GitLab `variables:` → GitHub `env:` (workflow-level) or `jobs.<id>.env:`
4. **Map secrets:** GitLab CI/CD variables (masked) → GitHub Secrets (`${{ secrets.NAME }}`)
5. **Map runners:** GitLab `tags: [docker]` → GitHub `runs-on: ubuntu-latest`
6. **Map images:** GitLab `image: node:18` → GitHub `container: node:18` (or use setup actions)
7. **Map artifacts:** GitLab `artifacts: paths:` → GitHub `actions/upload-artifact@v4`
8. **Map caching:** GitLab `cache:` → GitHub `actions/cache@v4`
9. **Map rules/only/except:** GitLab `rules:` → GitHub `on:` triggers + `if:` conditions
10. **Map services:** GitLab `services:` → GitHub `services:` in job

## Common Keyword Mapping

| GitLab CI | GitHub Actions |
|-----------|---------------|
| `stages:` | `jobs:` with `needs:` |
| `before_script:` | Step at start of `steps:` |
| `after_script:` | `if: always()` step at end |
| `script:` | `run:` in a step |
| `image:` | `container:` or setup action |
| `only: [main]` | `on: push: branches: [main]` |
| `when: manual` | `workflow_dispatch:` |
| `artifacts:` | `actions/upload-artifact@v4` |
| `cache: key:` | `actions/cache@v4` with `key:` |
| `variables:` | `env:` |
| `extends:` | Reusable workflows or composite actions |
| `include:` | Reusable workflows (`uses:`) |
| `needs:` | `needs:` (same concept) |
| `environment:` | `environment:` (same concept) |
| `allow_failure: true` | `continue-on-error: true` |

## Gotchas
- GitLab `extends:` has no exact equivalent — use reusable workflows or composite actions
- GitLab `include:` can reference local files — GitHub uses `uses:` with repo references
- GitLab `rules:changes:` → GitHub `paths:` filter in `on.push`
- GitLab `parallel:` matrix → GitHub `strategy.matrix:`
- GitLab `artifacts:expire_in:` → GitHub artifacts expire after 90 days by default
- GitLab `trigger:` for downstream pipelines → GitHub `workflow_call` events

## Validation Criteria
- No `.gitlab-ci.yml` remains
- All `.github/workflows/*.yml` pass `actionlint`
- All secrets use `${{ secrets.* }}` syntax (never hardcoded)
- All jobs have valid `runs-on:` values
- Workflow triggers match original CI behavior

## Related
- [[github-actions-workflow]]
