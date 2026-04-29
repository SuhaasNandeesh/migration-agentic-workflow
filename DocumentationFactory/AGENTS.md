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

### Agent Architecture
- **Supervisor (`doc-supervisor`)** is the primary orchestrator. It manages the sequence and enforces the disk-based handover state machine.
- No agent may pause or wait for human input. If a file is unreadable, log a warning and continue.
