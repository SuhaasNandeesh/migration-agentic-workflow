# Pipeline Migration Patterns (Examples)

> These are EXAMPLE patterns for translating between CI/CD formats. Handle any pipeline format using structural analysis.

## GitLab CI → GitHub Actions

| GitLab CI Concept | GitHub Actions Equivalent |
|-------------------|--------------------------|
| `.gitlab-ci.yml` | `.github/workflows/<name>.yml` |
| `stages:` | Implicit via `jobs:` + `needs:` |
| `image:` | `runs-on:` + `container:` |
| `script:` | `steps: - run:` |
| `before_script:` | Early `steps:` entries |
| `after_script:` | Step with `if: always()` |
| `variables:` | `env:` (workflow, job, or step level) |
| `cache:` | `actions/cache@v4` |
| `artifacts:` | `actions/upload-artifact@v4` / `actions/download-artifact@v4` |
| `rules: - if:` | `if:` condition on job |
| `only: / except:` | `on:` workflow triggers + job `if:` |
| `environment:` | `environment:` with protection rules |
| `services:` | `services:` in job container config |
| `needs:` | `needs:` (same concept) |
| `extends:` | Reusable workflows (`workflow_call`) |
| `include:` | Reusable workflows or composite actions |
| `trigger:` | `workflow_dispatch` or `repository_dispatch` |

## Jenkins → GitHub Actions

| Jenkins Concept | GitHub Actions Equivalent |
|----------------|--------------------------|
| `Jenkinsfile` | `.github/workflows/<name>.yml` |
| `pipeline { }` | `name:` + `on:` + `jobs:` |
| `agent any` | `runs-on: ubuntu-latest` |
| `agent { docker { image '...' } }` | `container: image: ...` |
| `stages { stage('...') { } }` | `jobs:` with descriptive names |
| `steps { sh '...' }` | `steps: - run: ...` |
| `environment { }` | `env:` |
| `parameters { }` | `workflow_dispatch: inputs:` |
| `when { branch 'main' }` | `on: push: branches: [main]` |
| `post { always { } }` | `if: always()` on step |
| `post { failure { } }` | `if: failure()` on step |
| `parallel { }` | Multiple jobs without `needs:` |
| `withCredentials([...])` | `secrets.*` in GitHub |
| `stash / unstash` | `upload-artifact / download-artifact` |

## Azure DevOps → GitHub Actions

| Azure DevOps Concept | GitHub Actions Equivalent |
|---------------------|--------------------------|
| `azure-pipelines.yml` | `.github/workflows/<name>.yml` |
| `trigger:` | `on: push:` |
| `pool: vmImage:` | `runs-on:` |
| `steps: - task:` | `steps: - uses:` |
| `steps: - script:` | `steps: - run:` |
| `variables:` | `env:` |
| `stages:` | `jobs:` with `needs:` |
| `template:` | Reusable workflows |

## CircleCI → GitHub Actions

| CircleCI Concept | GitHub Actions Equivalent |
|-----------------|--------------------------|
| `.circleci/config.yml` | `.github/workflows/<name>.yml` |
| `executors:` | `runs-on:` or `container:` |
| `orbs:` | `uses:` (actions) |
| `workflows:` | `on:` triggers + `jobs:` |
| `persist_to_workspace / attach_workspace` | `upload-artifact / download-artifact` |

## Cloud Authentication in Pipelines

| Source Pattern | Target (GitHub + Azure) |
|---------------|------------------------|
| AWS credentials (access key/secret) | Azure OIDC: `azure/login@v2` with federated credentials |
| GCP service account key JSON | Azure OIDC: `azure/login@v2` with federated credentials |
| Static credentials in env vars | `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` (OIDC) |

## General Rules
- Preserve ALL pipeline stages (build, test, security, deploy)
- Use OIDC for cloud authentication (never stored credentials)
- Pin action versions to commit SHA, not `@latest`
- Add `permissions:` block to limit `GITHUB_TOKEN` scope
- Any source-specific plugin/orb → find GitHub Action equivalent or shell script
