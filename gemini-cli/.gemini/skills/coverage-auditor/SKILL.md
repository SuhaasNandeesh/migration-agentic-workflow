---
name: coverage-auditor
description: "A Python skill that acts as a Deterministic Quality Gate. It cross-references the LLM's coverage tags against the Baseline Census to mathematically prove documentation completeness."
---
# Coverage Auditor

## Usage
Run the script to reconcile documentation coverage against the original dependency graph.

```bash
python3 .opencode/skills/coverage-auditor/run.py \
  --deps DocumentationFactory/output/artifacts/dependency-graph.json \
  --specs DocumentationFactory/output/artifacts/infrastructure-specs.json \
  --flows DocumentationFactory/output/artifacts/pipeline-flows.json
```

If the coverage drops below 95%, the script exits with status `1` and outputs the exact missing files.
