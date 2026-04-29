---
id: ecr-to-acr
severity: medium
last_updated: "2026-04-22"
source_runs: 0
---
# ECR Image References Must Be Updated to ACR

## Problem
After migrating from EKS to AKS, Kubernetes manifests and Dockerfiles may still reference
ECR (Elastic Container Registry) image URIs:
```
<account-id>.dkr.ecr.<region>.amazonaws.com/my-app:v1.2.3
```

AKS cannot pull from ECR without additional cross-cloud authentication setup.

## Fix
Replace all ECR references with ACR (Azure Container Registry):
```
<registry-name>.azurecr.io/my-app:v1.2.3
```

## Where to Check
- All Kubernetes Deployment/StatefulSet/DaemonSet manifests → `spec.template.spec.containers[].image`
- All Helm `values.yaml` → `image.repository`
- All `docker-compose.yml` → `image:` fields
- All `Dockerfile` → `FROM` statements that reference ECR
- All CI/CD pipelines → `docker push`/`docker pull` commands
- All shell scripts → `docker tag` / `docker push` commands

## Detection Pattern
```bash
grep -rn "dkr.ecr" --include="*.yaml" --include="*.yml" --include="*.tf" --include="Dockerfile*"
```

## Related
- [[kubernetes_deployment]]
- [[eks-to-aks-manifests]]
