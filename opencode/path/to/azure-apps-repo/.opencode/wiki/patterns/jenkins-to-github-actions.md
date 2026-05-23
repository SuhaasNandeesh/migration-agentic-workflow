---
pattern: jenkins-to-github-actions
complexity: functional
last_updated: "2026-04-22"
source_runs: 0
---
# Jenkins to GitHub Actions

## Migration Steps

1. **Replace file:** `Jenkinsfile` → `.github/workflows/<pipeline-name>.yml`
2. **Map pipeline structure:** `pipeline { stages { } }` → `jobs:` with `steps:`
3. **Map agent:** `agent { docker { image 'node:18' } }` → `runs-on: ubuntu-latest` + `container: node:18`
4. **Map stages to jobs:** Each `stage('Build')` → a `jobs.build:` entry
5. **Map steps:** `sh 'npm install'` → `run: npm install`
6. **Map credentials:** Jenkins credentials → GitHub Secrets
7. **Map parameters:** `parameters { string(...) }` → `workflow_dispatch: inputs:`
8. **Map post actions:** `post { always { } }` → steps with `if: always()`
9. **Map parallel stages:** `parallel { }` → separate jobs without `needs:` dependencies
10. **Map shared libraries:** `@Library('shared')` → reusable workflows or composite actions

## Common Mapping

| Jenkins | GitHub Actions |
|---------|---------------|
| `pipeline { }` | Workflow YAML file |
| `agent any` | `runs-on: ubuntu-latest` |
| `stage('X')` | `jobs.x:` |
| `steps { sh 'cmd' }` | `steps: - run: cmd` |
| `environment { }` | `env:` |
| `withCredentials([...])` | `${{ secrets.NAME }}` |
| `when { branch 'main' }` | `on: push: branches: [main]` |
| `post { failure { } }` | `if: failure()` step |
| `input message: 'Deploy?'` | `environment:` with protection rules |
| `archiveArtifacts` | `actions/upload-artifact@v4` |
| `publishHTML` | Upload to GitHub Pages or artifact |

## Gotchas
- Jenkins shared libraries have no direct equivalent — refactor into composite actions or reusable workflows
- Jenkins `Jenkinsfile` Groovy scripting → GitHub Actions has limited expression syntax
- Jenkins parameterized builds → `workflow_dispatch` with `inputs:`
- Jenkins credentials binding → GitHub Secrets (org/repo level)
- Jenkins plugins → GitHub Actions marketplace actions
- Jenkins multibranch pipeline → GitHub Actions triggers with `branches:` filter

## Validation Criteria
- No `Jenkinsfile` remains in codebase
- All workflows pass `actionlint`
- All secrets use `${{ secrets.* }}` syntax
- Workflow triggers cover all original build conditions

## Related
- [[gitlab-ci-to-github-actions]]
