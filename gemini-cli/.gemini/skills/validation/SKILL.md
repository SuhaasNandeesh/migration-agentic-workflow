---
name: validation
description: "Executes validation checks including syntax, execution, standards compliance, and migration completeness. Standards for multiple domains available in references/."
---
# Validation

Execute comprehensive validation checks on migration artifacts.

## Checks
1. **Syntax** — All files must be syntactically valid
2. **Execution** — Commands must complete successfully (terraform validate, kubectl dry-run)
3. **Standards Compliance** — Must pass all rules from `references/`
4. **Migration Completeness** — No source platform residue, full resource coverage

## Available Standards (in references/)
- `references/terraform.md` — Terraform validation + migration cleanup rules
- `references/kubernetes.md` — K8s requirements + platform-specific rules
- `references/pipelines.md` — CI/CD pipeline structure + auth requirements
- `references/security.md` — DevSecOps rules (secrets, identity, encryption, network)
- `references/tooling.md` — Preferred tools and consistency rules
- `references/migration.md` — Migration completeness and source cleanup rules
- `references/github-actions.md` — GitHub Actions-specific standards
- `references/target-platform.md` — Target platform naming, tags, identity rules