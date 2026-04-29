REQUIRED:
- resource limits (cpu, memory)
- resource requests (cpu, memory)
- liveness probe
- readiness probe
- pod disruption budget (for production workloads)
- service account (never use default)

LABELS (required on all resources):
- app.kubernetes.io/name
- app.kubernetes.io/version
- app.kubernetes.io/component
- app.kubernetes.io/managed-by

SECURITY:
- no privileged containers (privileged: false)
- no hostNetwork unless documented justification
- no hostPID, no hostIPC
- runAsNonRoot: true
- readOnlyRootFilesystem: true (where possible)
- drop ALL capabilities, add only what's needed
- use namespaces for isolation

IMAGES:
- No "latest" tags — use specific version or digest
- Images must reference target platform container registry
- No source platform container registry references

IDENTITY:
- Use target platform workload identity mechanism (not static secrets)
- Service accounts must have minimal RBAC permissions
- No source platform identity annotations

STORAGE:
- Use target platform CSI drivers
- No source platform CSI driver references
- Storage classes must reference target platform

NETWORKING:
- Use target platform ingress controller
- No source platform load balancer annotations
- Network policies should be defined for all namespaces

MIGRATION-SPECIFIC:
- No source platform annotations remaining
- No source platform-specific labels
- No source platform service endpoints in configs

FAIL IF:
- Missing resource limits or requests
- Missing probes
- Privileged container detected
- "latest" image tag used
- Source platform references found