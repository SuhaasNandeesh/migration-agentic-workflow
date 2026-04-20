# CodeMigration — Project Rules

## Execution Mode
- **Autonomous end-to-end execution** — agents must complete the full pipeline without pausing for human approval
- Agents must create, write, and validate all required files to produce a deployment-ready bundle
- Human intervention is only required at final deployment — never during generation or validation

## Global Rules
- Agents must use `rag-query` skill before execution
- Standards (in `validation/references/`) must always be enforced
- Outputs must be structured JSON
- All failures must be logged
- Agents must write artifacts to disk — do not return file contents as text responses
- No actual deployment or infrastructure provisioning — generate files only

## Execution Workflow

The multi-agent pipeline follows this sequence autonomously:

1. **Source Analyzer** — Scans source codebase and inventories all resources
2. **Migration Mapper** — Maps source resources to target platform equivalents
3. **Planner** — Converts mapping into ordered execution plan (migration waves)
4. **Developer** — Generates and writes target platform files to disk
5. **Code Reviewer** — Reviews migration accuracy and functional equivalence
6. **QA Tester** — Runs real validation tools (terraform, kubectl, linters)
7. **Validator** — Enforces standards compliance
8. **Security** — Enforces DevSecOps practices
9. **Documentation** — Generates runbooks, mapping docs, ADRs, deployment guides
10. **Evaluator** — Measures migration completeness and quality
11. **Packager** — Assembles all artifacts into a deployment-ready bundle
12. **Memory Writer** — Persists useful knowledge for future runs
13. **Feedback** — Suggests improvements based on metrics

### Flow Control
- If validation fails → retry (max 3) — **do not pause for human input**
- If still fails → stop and log the failure with full details
- Only pass → continue to next step automatically

## Agent Architecture
- **Supervisor** is the primary orchestrating agent
- All other agents are subagents delegated to by the supervisor
- The supervisor enforces the state machine and never generates artifacts directly
- **No agent may pause, ask for confirmation, or wait for human approval during execution**

## Migration Configuration
- Source and target platforms configured in `migration-config.json` at project root
- Mapping references in `migration-mapping/references/` are EXAMPLES — agents handle any resource
- Standards in `validation/references/` are enforceable rules
- Templates in `context-builder/assets/templates/` are starting points, not rigid structures
- New migration paths can be added by creating new reference files

## Design Principles
- **Platform-agnostic agents** — agents handle any source→target migration
- **Discovery-based** — agents scan and discover, not assume
- **Extensible** — new tools/platforms added via configuration and reference files
- **Self-improving** — feedback agent captures patterns for future runs
