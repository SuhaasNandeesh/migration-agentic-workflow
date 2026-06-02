# CI/CD → Azure DevOps Pipelines

A common AWS→Azure migration retargets CI to **Azure Pipelines** (`azure-pipelines.yml`) instead of GitHub Actions. Use this when the org standardizes on Azure DevOps.

| Source concept | Azure Pipelines equivalent |
|---|---|
| GitLab `stages:` / Jenkins stages | `stages:` → `jobs:` → `steps:` |
| Jenkins agent / GH `runs-on` | `pool: { vmImage: 'ubuntu-latest' }` |
| Secrets / env | Variable Groups (linked to Key Vault) + `$(VarName)` |
| Cloud auth (AWS keys) | **Azure service connection + Workload Identity Federation (OIDC)** — no stored secrets |
| Artifacts | `PublishPipelineArtifact@1` / `DownloadPipelineArtifact@1` |

## Golden Example (`azure-pipelines.yml`)
```yaml
trigger:
  branches: { include: [ main ] }

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: Build
    jobs:
      - job: build
        steps:
          - task: TerraformInstaller@1
            inputs: { terraformVersion: 'latest' }
          - script: terraform init -backend=false && terraform validate
            displayName: 'Terraform validate'
  - stage: Deploy
    dependsOn: Build
    jobs:
      - deployment: deploy
        environment: 'prod'                       # gated environment + approvals
        strategy: { runOnce: { deploy: { steps: [
          - task: AzureCLI@2
            inputs:
              azureSubscription: 'sc-prod-oidc'    # service connection using Workload Identity Federation
              scriptType: bash
              scriptLocation: inlineScript
              inlineScript: 'az account show'
        ] } } }
```

## Gotchas
- **No good offline linter** for Azure Pipelines YAML (actionlint is GitHub-only) — validate with `yamllint` + Azure DevOps server-side validation (`az pipelines validate` or the editor). Treat structural checks as best-effort.
- Use **Workload Identity Federation (OIDC) service connections** — never store AWS/Azure keys in variables.
- Map GH Actions `permissions: id-token: write` → an OIDC-enabled **service connection**; map secrets → **Variable Groups backed by Key Vault**.
