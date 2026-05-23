---
name: context-builder
description: "Constructs minimal, relevant, and structured context for agent execution. Provides migration templates, standards references, and memory data. Templates cover Azure Terraform, AKS K8s, and GitHub Actions."
metadata:
  version: "2.0"
---
# Context Builder

Construct minimal, relevant, and structured context for agent execution.

## Input
- task
- rag_results
- migration_config (from migration-config.json)

## Output Schema
```json
{
  "task": "",
  "context": [],
  "constraints": [],
  "migration": {
    "source_platform": "",
    "target_platform": ""
  }
}
```

## Context Sources
- `validation/references/*` (enforceable standards)
- `migration-mapping/references/*` (mapping patterns)
- `memory-store/assets/*` (past learnings)
- `context-builder/assets/templates/*` (code templates)

## Selection Rules
- Select top 5 MOST relevant items (expanded for migration context)
- Prioritize in order:
  1. Applicable standards for the target platform
  2. Migration mapping patterns for the source→target combination
  3. Templates for the target platform
  4. Past successful patterns from memory
- Ignore unrelated data

## Mandatory Constraints
Always include:
- "follow standards strictly"
- "no hardcoded secrets"
- "no source platform references in output"
- "output must be structured"

## Templates Available

### Terraform (Azure target)
- `assets/templates/terraform/azure_module.tf` — Azure module with azurerm provider
- `assets/templates/terraform/azure_backend.tf` — Azure Storage backend
- `assets/templates/terraform/base_module.tf` — Generic module scaffold
- `assets/templates/terraform/variables.tf` — Variable definitions

### Kubernetes (AKS target)
- `assets/templates/kubernetes/aks_deployment.yaml` — AKS deployment with Workload Identity
- `assets/templates/kubernetes/deployment.yaml` — Generic K8s deployment

### Pipelines (GitHub Actions target)
- `assets/templates/pipelines/github_actions_ci.yml` — CI workflow with OIDC + Trivy
- `assets/templates/pipelines/github_actions_cd.yml` — CD workflow with environment protection
- `assets/templates/pipelines/base_pipeline.yaml` — Generic pipeline stages
