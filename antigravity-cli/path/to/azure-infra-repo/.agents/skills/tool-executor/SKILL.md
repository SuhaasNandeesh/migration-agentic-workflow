---
name: tool-executor
description: "Executes real tools and scripts for validation purposes. Captures stdout/stderr and returns exit status. Scripts available in scripts/ directory."
---
# Tool Executor

Execute real tools for validation.

## Input
- command

## Output Schema
```json
{
  "status": "success|fail",
  "logs": ""
}
```

## Available Scripts
- `scripts/terraform_executor.sh` — Runs terraform fmt, validate, plan
- `scripts/pipeline_linter.sh` — Checks pipeline structure for security stage

## Rules
- Capture stdout and stderr
- Return exit status
- DO NOT ignore failures
