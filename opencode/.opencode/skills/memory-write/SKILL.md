---
name: memory-write
description: "Writes structured memory entries to the memory store after successful task completion."
metadata:
  version: "1.0"
---
# Memory Write

Write structured memory entries to `memory-store/assets/`.

## Output Format
```json
{
  "problem": "",
  "fix": "",
  "tags": [],
  "confidence": ""
}
```

## Target Locations
- Structured entries → `memory-store/assets/structured/issues.json`
- Documentation → `memory-store/assets/docs/issues_and_fixes.md`
- Execution traces → `memory-store/assets/traces/`
