# CodeMigration — Project Rules

## Execution Mode
- **Autonomous end-to-end execution** — agents must complete the full pipeline without pausing for human approval
- Agents must create, write, and validate all required files to produce a deployment-ready bundle
- Human intervention is only required at final deployment — never during generation or validation

## Global Rules
- **Categorized Knowledge Routing:** Agents must read their domain-specific knowledge file from `knowledge/` before execution to prevent context bloat and data loss.
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
13. **Shared Memory Writer** — Distills categorized knowledge to the global patterns base
14. **Git Publisher** — Safely commits and conditionally pushes to a feature branch
15. **Feedback** — Suggests improvements based on metrics

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

---

# Codebase Documentation Factory — Project Rules

## Execution Mode
- **Autonomous end-to-end execution** — agents must complete the full documentation pipeline without pausing for human approval.
- Agents operate strictly in a **read-only capacity** against the source code. They are forbidden from modifying infrastructure, pipelines, or application code.
- All generated documentation is written to `DocumentationFactory/output/docs/` in standard Markdown format.

## Global Rules
- **Comprehensive yet Concise:** Documentation must cover all necessary technical details and concepts (inputs, outputs, architecture, control flows) without unnecessary fluff.
- **Visual Mapping:** Complex topologies and CI/CD flows must be represented using Mermaid.js code blocks.
- **Context Management:** Agents must heavily utilize disk-based I/O (`output/artifacts/`) to hand over large chunks of data (like file dependencies) to prevent LLM context bloat.
- **Deterministic Coverage Matrix:** The pipeline enforces a strict 95% minimum coverage threshold. A python script audits the LLM's generated `files_covered` tags against a baseline census. Any score below 95% fails the build.

## Execution Workflow
The pipeline runs sequentially, but utilizes **Wave-Based Micro-Batching** to handle massive codebases without exhausting context windows:

1. **Discovery Scanner** — Scans the repository. Categorizes files generically (IaC, App Code, Orchestration) and outputs a global dependency graph.
2. **Doc Planner** — Reads the dependency graph and splits the documentation effort into small batches (Waves).
3. **WAVE LOOP (Executed sequentially per batch):**
   - **Spec Analyst** — Generates detailed Markdown specs. Embeds `files_covered` trace tags.
   - **Flow Tracer** — Analyzes logic flows. Embeds `files_covered` trace tags.
   - **Variable Extractor** — Builds a Global Data Dictionary and explicitly flags hardcoded secrets.
   - **Doc Reviewer (Deterministic Gate)** — Runs the `coverage-auditor` script. Compares the generated spec tags against the baseline census. Enforces the 95% threshold.
   - **Doc Surgical Fix** — If the reviewer fails, surgically patches the missing files listed by the auditor.
4. **Topology Mapper** — Post-wave, reads the aggregated data to generate system architecture diagrams using Mermaid.js.
5. **Doc Assembler** — Stitches the outputs into a cohesive, interlinked standard Markdown wiki.
6. **Site Builder** — Runs deterministic Markdown linting, dead-link auditing (`lychee`), and compiles the `mkdocs` static site.
7. **Doc Git Publisher** — Commits the final static site and safely pushes to a Git branch.

### Agent Architecture
- **Supervisor (`doc-supervisor`)** is the primary orchestrator. It manages the sequence and enforces the disk-based handover state machine.
- No agent may pause or wait for human input. If a file is unreadable, log a warning and continue.
