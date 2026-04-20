DEVSECOPS RULES:

SECRETS:
- No hardcoded secrets in any file (API keys, passwords, tokens, connection strings)
- All secrets must be stored in vault / key management service
- No base64-encoded secrets as a substitute for proper vault usage
- Pipeline secrets via OIDC or platform-native secret injection

IDENTITY & ACCESS:
- Use managed identity / workload identity — never static credentials
- Apply principle of least privilege for all IAM/RBAC assignments
- Prefer platform built-in roles over custom role definitions
- Service accounts must have explicit, minimal permissions
- No wildcard permissions (*) in any role definition

NETWORK SECURITY:
- Default deny — explicitly allow required traffic only
- All public endpoints must have WAF or DDoS protection
- TLS 1.2+ mandatory for all endpoints
- No open security group rules (0.0.0.0/0) without WAF
- Database firewall rules must restrict access to application subnets only

ENCRYPTION:
- Encryption at rest mandatory for all storage and databases
- Encryption in transit (TLS) mandatory for all communication
- Use platform-managed keys or customer-managed keys in vault

CONTAINER SECURITY:
- No privileged containers
- No root user in containers (runAsNonRoot: true)
- Container images scanned for vulnerabilities before deployment
- Only trusted registries allowed
- No "latest" tags — reproducible builds require pinned versions

PIPELINE SECURITY:
- SAST (Static Application Security Testing) step required
- Dependency scanning step required
- Container image scanning step required
- Secret scanning step required
- All of the above must PASS for pipeline to continue

AUDIT & COMPLIANCE:
- Audit logging must be enabled for all critical resources
- All resource changes must be traceable
- Compliance policies must be applied (platform-native policy engine)

MIGRATION-SPECIFIC:
- No source platform credentials remaining in any file
- No source platform endpoints or identifiers
- All source platform security mechanisms replaced with target equivalents

FAIL IF:
- Hardcoded secret detected
- Static credentials used for cloud authentication
- Missing encryption configuration
- Privileged container detected
- Missing security scanning pipeline step
- Source platform security patterns unreplaced