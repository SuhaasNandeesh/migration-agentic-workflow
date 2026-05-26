---
name: ast-stubber
description: "A Python skill that parses massive files, generates lightweight folded structural stubs, and supports JIT block hydration to keep agent contexts clean."
---
# AST Code Stubber & JIT Hydration Skill

This skill allows agents to dynamically compress large files (>= 1,000 lines of code) into structural skeletons, and selectively hydrate/restore raw code sections when editing.

## Usage

### 1. Generate a Folded Stub
Creates a lightweight structural outline of a target file. All inactive method/block bodies are minified.

```bash
python3 .gemini/skills/ast-stubber/run.py --file /path/to/large/file.tf --stub --output output/artifacts/stubs/large/file.tf
```

### 2. Hydrate/Expand a Block JIT
Restores the raw content of a specific block/region or line range within a stub file for zero-loss editing.

```bash
python3 .gemini/skills/ast-stubber/run.py --file /path/to/large/file.tf --hydrate --line-range 120-165
```

Alternatively, hydrate by specific block name or identifier:

```bash
python3 .gemini/skills/ast-stubber/run.py --file /path/to/large/file.tf --hydrate --block-name aws_db_instance.primary
```
