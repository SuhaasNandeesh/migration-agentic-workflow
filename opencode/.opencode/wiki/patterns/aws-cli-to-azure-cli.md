---
pattern: aws-cli-to-azure-cli
complexity: functional
last_updated: "2026-04-22"
source_runs: 0
---
# AWS CLI to Azure CLI — Shell Script Migration

## Common Command Mapping

### Identity & Auth
| AWS CLI | Azure CLI |
|---------|-----------|
| `aws sts get-caller-identity` | `az account show` |
| `aws configure` | `az login` |
| `aws iam create-role` | `az identity create` / `az role assignment create` |

### Compute
| AWS CLI | Azure CLI |
|---------|-----------|
| `aws ec2 describe-instances` | `az vm list` |
| `aws ec2 run-instances` | `az vm create` |
| `aws ec2 terminate-instances` | `az vm delete` |
| `aws ec2 start-instances` | `az vm start` |
| `aws ec2 stop-instances` | `az vm stop` |

### Networking
| AWS CLI | Azure CLI |
|---------|-----------|
| `aws ec2 describe-vpcs` | `az network vnet list` |
| `aws ec2 create-vpc` | `az network vnet create` |
| `aws ec2 describe-subnets` | `az network vnet subnet list` |
| `aws ec2 describe-security-groups` | `az network nsg list` |

### Storage
| AWS CLI | Azure CLI |
|---------|-----------|
| `aws s3 ls` | `az storage blob list` |
| `aws s3 cp` | `az storage blob upload` / `az storage blob download` |
| `aws s3 sync` | `az storage blob sync` (or `azcopy sync`) |
| `aws s3 mb s3://bucket` | `az storage container create` |
| `aws s3 rb s3://bucket` | `az storage container delete` |

### Container Registry
| AWS CLI | Azure CLI |
|---------|-----------|
| `aws ecr get-login-password \| docker login` | `az acr login --name <registry>` |
| `aws ecr create-repository` | `az acr create` |
| `aws ecr describe-repositories` | `az acr repository list` |

### Kubernetes
| AWS CLI | Azure CLI |
|---------|-----------|
| `aws eks update-kubeconfig` | `az aks get-credentials` |
| `aws eks describe-cluster` | `az aks show` |
| `aws eks list-clusters` | `az aks list` |

### Databases
| AWS CLI | Azure CLI |
|---------|-----------|
| `aws rds describe-db-instances` | `az sql server list` / `az postgres server list` |
| `aws dynamodb list-tables` | `az cosmosdb sql database list` |

## Script Migration Rules
1. Replace `aws` commands with `az` equivalents
2. Replace `--region us-east-1` with `--location eastus`
3. Replace `--profile` with Azure subscription context (`az account set`)
4. Replace AWS ARNs with Azure resource IDs (`/subscriptions/.../resourceGroups/...`)
5. Replace `jq` filters for AWS JSON output → adapt for Azure JSON output (different schema)
6. Replace `AWS_*` environment variables with `AZURE_*` equivalents
7. Replace `s3://bucket/key` URIs with Azure blob URIs

## Environment Variable Mapping
| AWS | Azure |
|-----|-------|
| `AWS_ACCESS_KEY_ID` | `AZURE_CLIENT_ID` |
| `AWS_SECRET_ACCESS_KEY` | `AZURE_CLIENT_SECRET` |
| `AWS_DEFAULT_REGION` | `AZURE_DEFAULTS_LOCATION` |
| `AWS_ACCOUNT_ID` | `AZURE_SUBSCRIPTION_ID` |
| `AWS_SESSION_TOKEN` | `AZURE_TENANT_ID` |

## Validation Criteria
- No `aws ` commands remain in scripts
- No AWS ARNs or account IDs remain
- No `AWS_*` environment variables remain
- All `az` commands are valid (check with `az <cmd> --help`)
- All scripts are executable and pass `shellcheck`
