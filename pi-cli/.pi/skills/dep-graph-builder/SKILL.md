---
name: dep-graph-builder
description: "A Python skill that scans a directory, identifies monorepo structures, and builds a JSON dependency graph of IaC, App Logic, and CI/CD files."
---
# Dependency Graph Builder

## Usage
Run the script to analyze the target directory and generate `dependency-graph.json`.

```bash
python3 .opencode/skills/dep-graph-builder/run.py --source /path/to/repo --output DocumentationFactory/output/artifacts/dependency-graph.json
```

The script specifically supports **Monorepo** structures by scanning for independent package directories (`apps/`, `packages/`, `services/`) and mapping intra-repo dependencies.
