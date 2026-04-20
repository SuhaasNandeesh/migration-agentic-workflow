---
name: context-optimizer
description: "Provides patterns for compressing agent outputs into lean summaries for context handover. Reduces token usage by 80-90% while preserving complete data on disk."
metadata:
  version: "1.0"
---
# Context Optimizer

Compress agent outputs for lean context handover between pipeline steps.

## Purpose
Multi-agent pipelines accumulate context with each step. Without compression,
a 13-step pipeline can reach 400K+ tokens, causing model degradation.
This skill provides patterns to keep supervisor context under 50K tokens
with zero data loss.

## Core Principle
**Full data on disk. Summaries in context.**

## Compression Patterns

### Pattern 1: Source Inventory Compression
```
FULL (5000+ tokens):
{"inventory": {"infrastructure": [{"file": "vpc.tf", "type": "terraform", "provider": "aws", 
"resources": [{"resource_type": "aws_vpc", "name": "main", "key_config": {"cidr_block": "10.0.0.0/16"}, 
"dependencies": ["aws_subnet.private", "aws_subnet.public"]}...]}...]}}

COMPRESSED (50 tokens):
"47 resources: 24 terraform, 12 k8s, 8 pipelines, 3 monitoring across 6 modules. 
Full: output/artifacts/source-inventory.json"
```

### Pattern 2: Migration Mapping Compression
```
FULL (4000+ tokens):
{"mappings": [{"source": "aws_vpc", "target": "azurerm_virtual_network", "tier": "direct", 
"config_changes": [...], "notes": "..."}, ...]}

COMPRESSED (40 tokens):
"45 direct maps, 2 redesign, 1 retain. 
Full: output/artifacts/migration-mapping.json"
```

### Pattern 3: Review/Test Results Compression
```
FULL (3000+ tokens):
{"status": "fail", "reviews": [{"file": "vpc.tf", "status": "pass"}, 
{"file": "compute.tf", "status": "fail", "issues": [{"severity": "critical", 
"message": "hardcoded AMI"}]}...]}

COMPRESSED (60 tokens):
"FAIL: 2 critical (hardcoded AMI in compute.tf, missing tags in lb.tf), 
3 pass. Full: output/artifacts/code-review-results.json"
```

### Pattern 4: Execution Plan Compression
```
FULL (3000+ tokens):
{"migration_waves": [{"wave": 0, "name": "Foundation", "modules": ["network", "nat"], 
"tasks": [{"id": "task-001", "module": "network", ...}]}...]}

COMPRESSED (50 tokens):
"4 waves, 6 tasks: Foundation(network,nat) → Security(sg,iam) → 
Compute(compute) → Routing(lb). Full: output/artifacts/execution-plan.json"
```

### Pattern 5: Security Scan Compression
```
FULL (2000+ tokens):
{"passed": [...], "issues": [{"severity": "medium", "description": "..."}...]}

COMPRESSED (40 tokens):
"PASS: 5 checks passed, 1 medium (missing egress rules). 
Full: output/artifacts/security-results.json"
```

## Summary Template
Every compressed summary must follow this format:
```
"<STATUS>: <key metric>. <critical details if any>. Full: <file path>"
```

Examples:
- "PASS: 47 resources found across 6 modules. Full: output/artifacts/source-inventory.json"
- "FAIL: 2 critical issues in compute module. Full: output/artifacts/code-review-results.json"
- "DONE: 24 files generated across 6 modules. Full: output/artifacts/generated-files.json"

## Rules
- Summary MUST be 1-2 lines maximum (under 100 tokens)
- Summary MUST include: status, key count/metric, and file path
- Summary MUST mention critical/blocking issues if any
- Full data MUST be written to disk BEFORE returning summary
- File paths MUST use the `output/artifacts/` convention
