PREFERRED TOOLS:

STATIC ANALYSIS (SAST):
- SonarQube (primary)
- CodeQL (for GitHub-integrated scanning)
- Semgrep (lightweight alternative)

DEPENDENCY SCANNING:
- Dependabot (GitHub-native)
- Trivy (multi-purpose)
- Snyk (if licensed)

SECRET SCANNING:
- GitHub Secret Scanning (GitHub-native, mandatory)
- gitleaks (additional layer)
- truffleHog (historical scan)

CONTAINER SCANNING:
- Trivy (primary)
- Platform-native container scanning (if available)

IAC SCANNING:
- tfsec (Terraform-specific)
- checkov (multi-framework: Terraform, K8s, CloudFormation, Helm)
- terrascan (policy-as-code)

KUBERNETES VALIDATION:
- kubeconform (schema validation, replaces kubeval)
- kubectl --dry-run (API validation)
- OPA / Gatekeeper (policy enforcement)

PIPELINE VALIDATION:
- actionlint (GitHub Actions)
- yamllint (generic YAML)

CODE QUALITY:
- hadolint (Dockerfiles)
- shellcheck (shell scripts)

OBSERVABILITY:
- Grafana (dashboards — portable)
- Prometheus (metrics — portable)
- Loki (logs — portable)
- Jaeger or Tempo (tracing — portable)

RULES:
- Use consistent tools across ALL services — no per-service tool divergence
- Prefer portable/OSS tools over cloud-native when possible
- Every tool choice should have a documented justification
- When adding a new tool, check if an existing tool covers the use case
- Tool versions must be pinned in pipeline configs