---
name: migration-mapping
description: "Provides pattern-based guidance for mapping resources between cloud platforms. References are EXAMPLES — agents should use LLM knowledge for resources not listed. Extensible for new platforms."
---
# Migration Mapping

Pattern-based guidance for mapping source platform resources to target platform equivalents.

## Important Design Principle
> The mapping references in `references/` are **examples and patterns**, NOT exhaustive lists.
> Agents MUST handle any resource type — including ones not listed — using their training knowledge.
> When encountering an unknown resource, map it by functional equivalence and set confidence to "low."

## How to Use
1. Load applicable mapping reference from `references/` based on source→target platforms
2. For resources found in the reference → use the documented mapping
3. For resources NOT in the reference → use LLM knowledge to determine equivalent
4. For resources with no equivalent → flag as "redesign required"
5. After migration, the feedback agent will suggest adding new patterns to references

## Available References
- `references/infrastructure-patterns.md` — Compute, storage, networking, database patterns
- `references/kubernetes-patterns.md` — K8s annotations, storage classes, identity patterns
- `references/pipeline-patterns.md` — CI/CD format translation patterns
- `references/observability-patterns.md` — Monitoring, logging, alerting patterns

## Adding New Migration Paths
To support a new source→target combination:
1. Create a new file in `references/` (e.g., `gcp-to-azure-patterns.md`)
2. Follow the same pattern: list common mappings as examples
3. The agents will automatically discover and use the new reference

## Confidence Levels
- **high:** Direct equivalent exists, well-documented mapping
- **medium:** Functional equivalent exists but configuration differs significantly
- **low:** Best-guess mapping, agent used training knowledge, should be reviewed
