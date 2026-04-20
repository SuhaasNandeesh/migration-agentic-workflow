---
name: source-analysis
description: "Provides tools and patterns for scanning and inventorying any source codebase. Includes file type detection patterns, resource extraction scripts, and dependency mapping guidance."
metadata:
  version: "1.0"
---
# Source Analysis

Tools and patterns for discovering what exists in a source codebase.

## File Detection Patterns

| Pattern | Type | Subtypes |
|---------|------|----------|
| `*.tf`, `*.tf.json` | Infrastructure as Code | Terraform |
| `*.yaml`, `*.yml` | Multi-purpose | K8s, Helm, CI/CD, monitoring |
| `Jenkinsfile`, `*.groovy` | Pipeline | Jenkins |
| `.gitlab-ci.yml` | Pipeline | GitLab CI |
| `.github/workflows/*.yml` | Pipeline | GitHub Actions |
| `azure-pipelines.yml` | Pipeline | Azure DevOps |
| `.circleci/config.yml` | Pipeline | CircleCI |
| `Dockerfile*` | Container | Docker |
| `docker-compose*.yml` | Container | Docker Compose |
| `Chart.yaml` | Package | Helm |
| `kustomization.yaml` | Package | Kustomize |
| `*.json` (with `AWSTemplateFormatVersion`) | IaC | CloudFormation |
| `*.bicep` | IaC | Bicep (Azure) |
| `Pulumi.yaml` | IaC | Pulumi |

## Provider Detection Patterns

| Pattern in Code | Platform |
|----------------|----------|
| `provider "aws"` or `aws_*` resources | AWS |
| `provider "azurerm"` or `azurerm_*` resources | Azure |
| `provider "google"` or `google_*` resources | GCP |
| `eks.amazonaws.com` annotations | AWS EKS |
| `azure.workload.identity` annotations | Azure AKS |
| `image: *.dkr.ecr.*.amazonaws.com` | AWS ECR |
| `image: *.azurecr.io` | Azure ACR |

## Discovery Rules
- Scan recursively — services may be in subdirectories
- Check for monorepo patterns (multiple `terraform/` dirs, multiple `k8s/` dirs)
- Parse `terraform.tfstate` if available for actual deployed resources (read-only)
- Check for `Chart.yaml` to identify Helm charts
- Check for `kustomization.yaml` to identify Kustomize overlays
- Any file not matching known patterns → categorize as "other" and report
