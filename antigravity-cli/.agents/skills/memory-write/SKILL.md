---
name: memory-write
description: "Writes structured memory entries to the memory store after successful task completion."
---
# Memory Write

Write structured memory entries securely to `memory-store/assets/` using the automated CLI tool.

## Usage
Run the execution script to append memories safely:
```bash
python3 .agents/skills/memory-write/run.py --problem "..." --fix "..." --tags "tag1,tag2" --confidence "high"
```

## target Locations Auto-Resolved
- Structured entries → `memory-store/assets/structured/issues.json`
- Documentation → `memory-store/assets/docs/issues_and_fixes.md`
- Execution traces → `memory-store/assets/traces/`
