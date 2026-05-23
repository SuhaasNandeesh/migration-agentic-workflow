---
name: code-review
description: "Provides review checklists and criteria for validating migration accuracy, code quality, and platform compliance."
metadata:
  version: "1.0"
---
# Code Review

Checklists and criteria for reviewing migrated code.

## Migration Accuracy Checklist
- [ ] Every source resource has a corresponding target resource
- [ ] Resource configurations are functionally equivalent (sizes, replicas, limits)
- [ ] Networking rules preserved (ports, protocols, CIDR ranges)
- [ ] Authentication/authorization is functionally equivalent
- [ ] Environment variables and configs are migrated
- [ ] Secrets are referenced via target platform vault/key management

## Source Platform Cleanup Checklist
- [ ] No source platform resource references in target code
- [ ] No source platform endpoints, ARNs, or account IDs
- [ ] No source platform CLI commands in scripts
- [ ] No source platform SDK references in application code
- [ ] No source platform container registry references

## Code Quality Checklist
- [ ] Variables used instead of hardcoded values
- [ ] Module structure is logical and follows target platform conventions
- [ ] Comments explain non-obvious migration decisions
- [ ] Naming follows target platform conventions
- [ ] No unnecessary complexity or dead code
